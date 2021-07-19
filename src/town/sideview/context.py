from math import sin, pi
import pygame
from lib.direction import invert as invert_direction

from contexts import Context
from contexts.dialogue import DialogueContext
from contexts.inventory import InventoryContext
from town.graph import TownGraph
from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.knight import Knight
from comps.hud import Hud
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from filters import replace_color, outline
from colors.palette import BLACK, WHITE, BLUE
from transits.dissolve import DissolveIn, DissolveOut
from anims import Anim
import keyboard

class FollowAnim(Anim): pass

def can_talk(hero, actor):
  if (not actor.get_message()
  or actor.get_faction() == "player"):
    return False
  hero_x, _ = hero.pos
  actor_x, _ = actor.pos
  dist_x = actor_x - hero_x
  facing_x, _ = hero.get_facing()
  return abs(dist_x) < TILE_SIZE * 1.5 and dist_x * facing_x >= 0

def find_nearby_npc(hero, actors):
  return next((a for a in actors if can_talk(hero, a)), None)

def find_nearby_link(hero, links, graph=None):
  hero_x, _ = hero.pos
  for link in links.values():
    dist_x = link.x - hero_x
    _, direction_y = link.direction
    if abs(dist_x) < TILE_SIZE // 2 and direction_y and not (graph and graph.tail(head=link) is None):
      return link

ARROW_Y = Area.ACTOR_Y + 40
ARROW_PERIOD = 45
ARROW_BOUNCE = 2

class SideViewContext(Context):
  def __init__(ctx, area, graph, party=[Knight()], spawn=None):
    super().__init__()
    ctx.area = area()
    ctx.party = [Actor(core=core) for core in party]
    ctx.spawn = spawn
    ctx.link = None
    ctx.talkee = None
    ctx.nearby_link = None
    ctx.nearby_npc = None
    ctx.hud = Hud(party)
    ctx.time = 0
    ctx.anims = []

  def init(ctx):
    hero, *_ = ctx.party
    if ctx.spawn:
      spawn_x = ctx.spawn.x
      hero.face(invert_direction(ctx.spawn.direction))
    else:
      spawn_x = 64
    facing_x, _ = hero.get_facing()
    for actor in ctx.party:
      ctx.area.spawn(actor, spawn_x)
      actor.stop_move()
      spawn_x -= TILE_SIZE * facing_x
    ctx.area.init(ctx)

  def handle_move(ctx, delta):
    hero, *allies = ctx.party
    hero.move((delta, 0))
    for i, ally in enumerate(allies):
      ally.follow(ctx.party[i])
    hero_x, hero_y = hero.pos
    for link_name, link in ctx.area.links.items():
      if (link.direction == (-1, 0) and hero.get_facing() == (-1, 0) and hero_x <= link.x
      or link.direction == (1, 0) and hero.get_facing() == (1, 0) and hero_x >= link.x):
        if ctx.use_link(link):
          break
    if hero_x < 0 and hero.get_facing() == (-1, 0):
      hero.pos = (0, hero_y)
    elif hero_x > ctx.area.width and hero.get_facing() == (1, 0):
      hero.pos = (ctx.area.width, hero_y)
    return True

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
    old_facing = talkee.get_facing()
    talkee.face(hero)
    message = talkee.get_message()
    if callable(message):
      message = message(ctx)
    def stop_talk():
      talkee.face(old_facing)
      ctx.talkee = None
    ctx.open(DialogueContext(script=message, on_close=stop_talk))
    return True

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if ctx.link or ctx.anims or ctx.get_head().transits:
      return False
    if key in (pygame.K_LEFT, pygame.K_a):
      return ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      return ctx.handle_move(1)
    if keyboard.get_pressed(key) > 1:
      return
    if key in (pygame.K_UP, pygame.K_w):
      return ctx.handle_zmove(-1)
    if key in (pygame.K_DOWN, pygame.K_s):
      return ctx.handle_zmove(1)
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      return ctx.handle_talk()

  def handle_keyup(ctx, key):
    if key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
      for actor in ctx.party:
        actor.stop_move()
      return True

  def get_graph(ctx):
    return ctx.parent.graph if "graph" in dir(ctx.parent) else None

  def use_link(ctx, link):
    graph = ctx.get_graph()
    if graph is None or graph.tail(head=link) is None:
      return False
    ctx.link = link
    if link.direction == (1, 0) or link.direction == (-1, 0):
      ctx.follow_link(ctx.link)
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
        try:
          if issubclass(dest_item, Context):
            ctx.parent.load_area(dest_item)
        except TypeError:
          dest_area = graph.link_area(link=dest_item)
          for actor in ctx.party:
            actor.stop_move()
          ctx.parent.load_area(dest_area, dest_item)
    else:
      ctx.close()

  def recruit(ctx, actor):
    actor.recruit()
    ctx.parent.recruit(actor.core)
    if len(ctx.party) == 1:
      ctx.party.append(actor)
    else:
      # TODO: handle party replacement
      ctx.party[1] = actor
    ctx.anims.append(FollowAnim(target=actor))
    ctx.nearby_npc = None

  def update(ctx):
    super().update()
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
            actor.move(link.direction)
        else:
          if hero_x != link.x:
            hero.move_to((link.x, hero_y))
          else:
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
        ctx.nearby_link = find_nearby_link(hero, ctx.area.links, ctx.get_graph())
        ctx.nearby_npc = find_nearby_npc(hero, ctx.area.actors) if ctx.nearby_link is None else None
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
      arrow_y = ARROW_Y + sin(ctx.time % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE
      sprites += [Sprite(
        image=arrow_image,
        pos=(link.x + ctx.area.camera, arrow_y),
        origin=("center", "center"),
        layer="markers"
      )]
    elif not interrupt and (npc := ctx.nearby_npc):
      npc_sprite = next((s for s in sprites if s.target is npc), None)
      if npc_sprite:
        npc_x, npc_y = npc_sprite.pos
        bubble_image = assets.sprites["bubble_talk"]
        bubble_x = npc_x + TILE_SIZE * 0.25
        bubble_y = npc_y - TILE_SIZE * 0.75
        sprites.append(Sprite(
          image=bubble_image,
          pos=(bubble_x, bubble_y),
          layer="markers"
        ))

    if sprites and sprites[0].image.get_width() == 256:
      for sprite in sprites:
        sprite.move((256 - WINDOW_WIDTH // 2, 0))
    sprites += ctx.hud.view()

    if ctx.time < 120 and not ctx.child:
      label_image = assets.ttf["roman"].render(ctx.area.name, WHITE)
      label_image = outline(label_image, BLACK)
      label_image = outline(label_image, WHITE)
      sprites.append(Sprite(
        image=label_image,
        pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
        origin=("center", "center"),
        layer="markers"
      ))

    return sprites + super().view()
