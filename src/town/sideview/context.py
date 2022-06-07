from math import sin, pi
from lib.direction import invert as invert_direction
import lib.vector as vector
import lib.input as input
from lib.line import find_lines_intersection, find_slope

from contexts import Context
from contexts.dialogue import DialogueContext
from contexts.inventory import InventoryContext
from town.sideview.stage import Area
from town.sideview.actor import Actor
from items.materials import MaterialItem
from comps.hud import Hud
from assets import load as use_assets
from lib.sprite import Sprite
from lib.filters import replace_color, outline
from colors.palette import BLACK, WHITE, BLUE
from transits.dissolve import DissolveIn, DissolveOut
from anims import Anim
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, LABEL_FRAMES

from town.graph import WorldGraph, WorldLink


class FollowAnim(Anim): pass

def can_talk(hero, actor):
  if (not actor.message
  or actor.faction == "player"):
    return False
  hero_x, hero_y = hero.pos
  actor_x, actor_y = actor.pos
  dist_x = actor_x - hero_x
  dist_y = actor_y - hero_y
  facing_x, _ = hero.facing
  return (
    abs(dist_y) <= TILE_SIZE / 2
    and abs(dist_x) < TILE_SIZE * 1.5
    and dist_x * facing_x >= 0
  )

def find_nearby_npc(hero, actors):
  return next((a for a in actors if can_talk(hero, a)), None)

def find_nearby_port(hero, area, graph=None):
  if not graph:
    return None

  for port_id, port in area.ports.items():
    dist_x, dist_y = vector.subtract((port.x, port.y), hero.pos)
    _, direction_y = port.direction
    if (not direction_y
    or abs(dist_x) > TILE_SIZE // 2
    or abs(dist_y) > TILE_SIZE // 2):
      continue

    link = WorldLink(type(area), port_id)
    if graph.tail(link):
      return port_id

ARROW_Y = Area.ACTOR_Y + 40
ARROW_PERIOD = 45
ARROW_BOUNCE = 2

class SideViewContext(Context):
  def __init__(ctx, store, area=None, spawn=None):
    super().__init__()
    ctx.area = area and area()
    ctx.store = store
    ctx.party = [Actor(core=core) for core in store.party]
    ctx.spawn = spawn
    ctx.ground = None
    ctx.port = None
    ctx.talkee = None
    ctx.nearby_port = None
    ctx.nearby_npc = None
    ctx.hud = Hud(store.party)
    ctx.time = 0
    ctx.anims = []

  def init(ctx):
    hero, *_ = ctx.party
    if ctx.spawn:
      hero.face(invert_direction(ctx.spawn.direction))
      spawn_x = ctx.spawn.x + TILE_SIZE * hero.facing[0]
      spawn_y = ctx.spawn.y
    else:
      spawn_x = 64
      spawn_y = 0
    facing_x, _ = hero.facing

    for actor in ctx.party:
      ctx.area and ctx.area.spawn(actor, spawn_x, spawn_y)
      actor.stop_move()
      spawn_x -= TILE_SIZE * facing_x

    ctx.area and ctx.area.init(ctx)
    ctx.hud.enter()

  def handle_move(ctx, delta):
    hero, *allies = ctx.party

    # adjust origin position to increase collision sensitivity
    old_hero_pos = vector.add(hero.pos, (0, -8))

    hero.move((delta, 0))
    if ctx.area.geometry:
      # angle velocity downwards to catch slopes
      hero.pos = vector.add(hero.pos, (0, 1))

    for i, ally in enumerate(allies):
      ally.follow(ctx.party[i])

    hero_x, hero_y = hero.pos

    for port_id, port in ctx.area.ports.items():
      if (port.direction == (-1, 0) and hero.facing == (-1, 0) and hero_x <= port.x
      or port.direction == (1, 0) and hero.facing == (1, 0) and hero_x >= port.x):
        if ctx.use_port(port_id):
          break

    if hero_x < 0 and hero.facing == (-1, 0):
      hero.pos = (0, hero_y)
    elif hero_x > ctx.area.width and hero.facing == (1, 0):
      hero.pos = (ctx.area.width, hero_y)

    if not ctx.area.geometry:
      return True

    line, _ = ctx.collide_hero(hero, old_pos=old_hero_pos)

    prev_ground = ctx.ground
    ctx.ground = line
    if prev_ground and line is None:
      hero_speed = hero.pos[0] - old_hero_pos[0]

      geometry_constraint_left = min(prev_ground[0][0], prev_ground[1][0])
      if hero.pos[0] <= geometry_constraint_left:
        hero.pos = (geometry_constraint_left, hero.pos[1])
        ctx.ground = prev_ground

      geometry_constraint_right = max(prev_ground[0][0], prev_ground[1][0])
      if hero.pos[0] >= geometry_constraint_right - hero_speed:
        hero.pos = (geometry_constraint_right, hero.pos[1])
        ctx.ground = prev_ground

    ctx.collide_hero(hero, old_pos=old_hero_pos)
    return True

  def collide_hero(ctx, hero, old_pos):
    hero_line = (old_pos, hero.pos)
    line, intersection = next(((line, intersection) for line in ctx.area.geometry if (intersection := find_lines_intersection(line, hero_line))), (None, None))
    if intersection:
      hproj, vproj = vector.subtract(hero.pos, intersection)
      slope = find_slope(line)
      hero.pos = vector.add(hero.pos, (0, -vproj - hproj * slope))

    return line, intersection

  def handle_zmove(ctx, delta):
    port_id = ctx.nearby_port
    if not port_id or port_id not in ctx.area.ports:
      return False

    port = ctx.area.ports[port_id]
    if port.direction[1] == delta:
      ctx.port = port_id
      return True
    else:
      return False

  def handle_talk(ctx):
    if ctx.nearby_npc is None:
      return False
    ctx.talkee = ctx.nearby_npc
    talkee = ctx.nearby_npc
    for actor in ctx.party:
      actor.stop_move()
    hero, *_ = ctx.party
    old_facing = talkee.facing
    talkee.face(hero)
    message = talkee.message
    if callable(message):
      message = message(ctx)
    def stop_talk():
      talkee.face(old_facing)
      ctx.talkee = None
    ctx.open(DialogueContext(script=message, side="top", on_close=stop_talk))
    return True

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.port or ctx.anims or ctx.get_head().transits:
      return False

    controls = input.resolve_controls(button)
    button = input.resolve_button(button)

    if button == input.BUTTON_LEFT:
      ctx.handle_move(-1)

    elif button == input.BUTTON_RIGHT:
      ctx.handle_move(1)

    if input.get_state(button) > 1:
      return

    if button == input.BUTTON_UP:
      for actor in ctx.party:
        actor.stop_move()
      return ctx.handle_zmove(-1)

    if button == input.BUTTON_DOWN:
      for actor in ctx.party:
        actor.stop_move()
      return ctx.handle_zmove(1)

    if input.CONTROL_CONFIRM in controls:
      return ctx.handle_talk()

  def handle_release(ctx, button):
    if ctx.child:
      return ctx.child.handle_release(button)

    button = input.resolve_button(button)
    if button in (input.BUTTON_LEFT, input.BUTTON_RIGHT):
      for actor in ctx.party:
        actor.stop_move()
      return True

  def use_item(ctx, item):
    if issubclass(item, MaterialItem):
      success, message = False, "You can't use this item!"
    else:
      success, message = ctx.store.use_item(item)
    if success:
      ctx.open(DialogueContext(
        lite=True,
        script=[
          ("", ("Used ", item.token(item), "\n", message)),
        ]
      ))
      return True, None
    else:
      return False, message

  def get_graph(ctx):
    return ctx.parent.graph if "graph" in dir(ctx.parent) else None

  def validate_port(ctx, port_id):
    graph = ctx.get_graph()
    return graph is not None and graph.tail(WorldLink(type(ctx.area), port_id)) is not None

  def use_port(ctx, port_id):
    if not ctx.validate_port(port_id):
      return False

    port = ctx.area.ports[port_id]
    if port.direction == (1, 0) or port.direction == (-1, 0):
      ctx.follow_port(port_id)
      ctx.area.lock_camera()

    ctx.port = port_id
    return True

  def follow_port(ctx, port_id):
    ctx.get_head().transition([
      DissolveIn(on_end=lambda: ctx.change_areas(port_id)),
      DissolveOut()
    ])

  def change_areas(ctx, port_id):
    graph = ctx.get_graph()
    if not graph:
      return ctx.close()

    src_link = WorldLink(type(ctx.area), port_id)
    dest_link = graph.tail(src_link)
    if not dest_link:
      return

    for actor in ctx.party:
      actor.stop_move()

    ctx.get_parent(cls="GameContext").load_area(dest_link.node, dest_link.port_id)
    ctx.port = None

  def switch_chars(ctx):
    ctx.store.switch_chars()
    ctx.party.reverse()

  def recruit(ctx, actor):
    actor.recruit()
    ctx.store.recruit(actor.core)
    if len(ctx.party) == 1:
      ctx.party.append(actor)
    else:
      # TODO: handle party replacement
      ctx.party[1] = actor
    ctx.anims.append(FollowAnim(target=actor))
    ctx.nearby_npc = None

  def update_interactives(ctx):
    hero = ctx.party[0]
    ctx.nearby_port = find_nearby_port(hero, ctx.area, graph=ctx.get_graph())
    ctx.nearby_npc = find_nearby_npc(hero, ctx.area.actors) if ctx.nearby_port is None else None

  def update(ctx):
    super().update()

    ctx.area.update()

    for actor in ctx.area.actors:
      actor.update()

    hero, *allies = ctx.party

    for anim in ctx.anims:
      if type(anim) is FollowAnim:
        done = anim.target.follow(hero, free=True, force=True)
        if done:
          anim.target.stop_move()
          anim.target.face(hero)
          ctx.anims.remove(anim)
        break
    else:
      if ctx.port:
        port_id = ctx.port
        port = ctx.area.ports[port_id]
        hero_x, hero_y = hero.pos
        if port.direction == (-1, 0) or port.direction == (1, 0):
          for actor in ctx.party:
            actor.move(port.direction)
        else:
          graph = ctx.get_graph()
          src_area = type(ctx.area)
          src_link = WorldLink(src_area, port_id)
          dest_link = graph and graph.tail(src_link)
          dest_area = dest_link.node
          dest_port = dest_link.port
          if dest_area == src_area:
            if hero.move_to(dest=(dest_port.x, dest_port.y), free=True):
              ctx.port = None
              ctx.update_interactives()
          else:
            if hero_x != port.x:
              hero.move_to((port.x, hero_y))
            else:
              if not ctx.area.is_camera_locked:
                ctx.area.lock_camera()

              if port.direction == (0, -1):
                TARGET_HORIZON = Area.HORIZON_NORTH
                EVENT_HORIZON = Area.TRANSIT_NORTH
              elif port.direction == (0, 1):
                TARGET_HORIZON = Area.HORIZON_SOUTH
                EVENT_HORIZON = Area.TRANSIT_SOUTH

              if hero_y != TARGET_HORIZON:
                hero.move_to((port.x, TARGET_HORIZON))

              if abs(hero_y) >= abs(EVENT_HORIZON) and not ctx.get_head().transits:
                ctx.follow_port(port_id)

          for ally in allies:
            ally.follow(hero)

      elif not ctx.child:
        ctx.update_interactives()

    ctx.hud.update(force=True)
    ctx.time += 1

  def view(ctx):
    sprites = []
    assets = use_assets()
    hero, *_ = ctx.party

    sprites += ctx.area.view(hero, ctx.port)
    interrupt = ctx.port or ctx.anims or (ctx.child
      and not isinstance(ctx.child, InventoryContext)
    )

    if interrupt:
      if ctx.hud.active:
        ctx.hud.exit()
    elif not ctx.hud.active:
      ctx.hud.enter()

    if not interrupt and ctx.nearby_port:
      port_id = ctx.nearby_port
      port = ctx.area.ports[port_id]
      arrow_image = (port.direction == (0, -1)
        and assets.sprites["port_north"]
        or assets.sprites["port_south"]
      )
      arrow_image = replace_color(arrow_image, BLACK, BLUE)
      arrow_y = (ARROW_Y
        + port.y
        + sin(ctx.time % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE)
      sprites += [Sprite(
        image=arrow_image,
        pos=vector.subtract((port.x, arrow_y), ctx.area.camera.rect.topleft),
        origin=Sprite.ORIGIN_CENTER,
        layer="markers"
      )]
    elif not interrupt and (npc := ctx.nearby_npc):
      npc_sprite = next((s for s in sprites if s.target is npc), None)
      if npc_sprite:
        npc_x, npc_y = npc_sprite.pos
        bubble_sheet = assets.sprites["bubble_talk"]
        bubble_image = bubble_sheet[int(ctx.time / 10) % len(bubble_sheet)]
        bubble_image = replace_color(bubble_image, BLACK, BLUE)
        bubble_x = npc_x + TILE_SIZE * 0.25
        bubble_y = npc_y - TILE_SIZE * 0.75
        sprites.append(Sprite(
          image=bubble_image,
          pos=(bubble_x, bubble_y),
          origin=Sprite.ORIGIN_BOTTOMLEFT,
          layer="markers"
        ))

    if sprites and sprites[0].image.get_width() == 256:
      for sprite in sprites:
        sprite.move((256 - WINDOW_WIDTH // 2, 0))
    sprites += ctx.hud.view()

    if ctx.time < LABEL_FRAMES and not ctx.child:
      label_image = assets.ttf["normal"].render(ctx.area.name, WHITE)
      label_image = outline(label_image, BLACK)
      sprites.append(Sprite(
        image=label_image,
        pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
        origin=("center", "center"),
        layer="markers"
      ))

    return sprites + super().view()
