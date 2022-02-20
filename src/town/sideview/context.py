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
    abs(dist_y) < 4
    and abs(dist_x) < TILE_SIZE * 1.5
    and dist_x * facing_x >= 0
  )

def find_nearby_npc(hero, actors):
  return next((a for a in actors if can_talk(hero, a)), None)

def find_nearby_link(hero, links, graph=None):
  for link in links.values():
    dist_x, dist_y = vector.subtract((link.x, link.y), hero.pos)
    _, direction_y = link.direction
    if (abs(dist_x) < TILE_SIZE // 2
    and abs(dist_y) < TILE_SIZE // 2
    and direction_y
    and (not graph or graph.tail(head=link) is not None)):
      return link

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
    ctx.link = None
    ctx.talkee = None
    ctx.nearby_link = None
    ctx.nearby_npc = None
    ctx.hud = Hud(store.party)
    ctx.time = 0
    ctx.anims = []

  def init(ctx):
    hero, *_ = ctx.party
    if ctx.spawn:
      spawn_x = ctx.spawn.x
      spawn_y = ctx.spawn.y
      hero.face(invert_direction(ctx.spawn.direction))
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

    for _, link in ctx.area.links.items():
      if (link.direction == (-1, 0) and hero.facing == (-1, 0) and hero_x <= link.x
      or link.direction == (1, 0) and hero.facing == (1, 0) and hero_x >= link.x):
        if ctx.use_link(link):
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
    link = ctx.nearby_link
    if link and link.direction[1] == delta:
      ctx.link = link
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

    if ctx.link or ctx.anims or ctx.get_head().transits:
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
      return ctx.handle_zmove(-1)

    if button == input.BUTTON_DOWN:
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

  def use_link(ctx, link):
    graph = ctx.get_graph()
    if graph is None or graph.tail(head=link) is None:
      return False
    ctx.link = link
    if link.direction == (1, 0) or link.direction == (-1, 0):
      ctx.follow_link(ctx.link)
      ctx.area.lock_camera()
    return True

  def follow_link(ctx, link):
    ctx.get_head().transition([
      DissolveIn(on_end=lambda: ctx.change_areas(link)),
      DissolveOut()
    ])

  def change_areas(ctx, link):
    if graph := ctx.get_graph():
      dest_item = graph.tail(head=link)
      if dest_item:
        for actor in ctx.party:
          actor.stop_move()
        if type(dest_item) is type and issubclass(dest_item, Context):
          ctx.parent.load_area(dest_item)
        else:
          dest_area = graph.link_area(link=dest_item)
          dest_area and ctx.parent.load_area(dest_area, dest_item)
        ctx.link = None
    else:
      ctx.close()

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
    ctx.nearby_link = find_nearby_link(hero, ctx.area.links, graph=ctx.get_graph())
    ctx.nearby_npc = find_nearby_npc(hero, ctx.area.actors) if ctx.nearby_link is None else None

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
      if link := ctx.link:
        hero_x, hero_y = hero.pos
        if link.direction == (-1, 0) or link.direction == (1, 0):
          for actor in ctx.party:
            if abs(actor.pos[0] - link.x) < TILE_SIZE:
              actor.move(link.direction)
        else:
          graph = ctx.get_graph()
          tail_link = graph and graph.tail(head=link)
          if tail_link and next((l for _, l in ctx.area.links.items() if l == tail_link), None):
            if hero.move_to(dest=(tail_link.x, tail_link.y), free=True):
              ctx.link = None
              ctx.update_interactives()
          else:
            if hero_x != link.x:
              hero.move_to((link.x, hero_y))
            else:
              if not ctx.area.is_camera_locked:
                ctx.area.lock_camera()

              if link.direction == (0, -1):
                TARGET_HORIZON = Area.HORIZON_NORTH
                EVENT_HORIZON = Area.TRANSIT_NORTH
              elif link.direction == (0, 1):
                TARGET_HORIZON = Area.HORIZON_SOUTH
                EVENT_HORIZON = Area.TRANSIT_SOUTH

              if hero_y != TARGET_HORIZON:
                hero.move_to((link.x, TARGET_HORIZON))

              if abs(hero_y) >= abs(EVENT_HORIZON) and not ctx.get_head().transits:
                ctx.follow_link(ctx.link)

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
    sprites += ctx.area.view(hero, ctx.link)
    interrupt = ctx.link or ctx.anims or (ctx.child
      and not isinstance(ctx.child, InventoryContext)
    )

    if interrupt:
      if ctx.hud.active:
        ctx.hud.exit()
    elif not ctx.hud.active:
      ctx.hud.enter()

    if not interrupt and (link := ctx.nearby_link):
      arrow_image = (link.direction == (0, -1)
        and assets.sprites["link_north"]
        or assets.sprites["link_south"]
      )
      arrow_image = replace_color(arrow_image, BLACK, BLUE)
      arrow_y = (ARROW_Y
        + link.y
        + sin(ctx.time % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE)
      sprites += [Sprite(
        image=arrow_image,
        pos=vector.subtract((link.x, arrow_y), ctx.area.camera.rect.topleft),
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
      label_image = outline(label_image, WHITE)
      sprites.append(Sprite(
        image=label_image,
        pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
        origin=("center", "center"),
        layer="markers"
      ))

    return sprites + super().view()
