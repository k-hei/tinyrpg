from contexts.prompt import PromptContext, Choice
from contexts.load import LoadContext
from contexts.save import SaveContext
from contexts.controls import ControlsContext
from contexts.nameentry import NameEntryContext


def handle_menus(name):
    return lambda ctx: [
        (name, "Hail, traveler!"),
        prompt := lambda: PromptContext("How fares the exploration?", (
            Choice("Manage data", closing=True),
            Choice("Edit controls"),
            Choice("Change name"),
            Choice("Nothing", closing=True)
        ), required=True, on_close=lambda choice: (
            choice.text == "Manage data" and [
            lambda: PromptContext("What would you like to do?", (
                Choice("Load data"),
                Choice("Save data"),
                Choice("Nothing", closing=True)
            ), required=True, on_close=lambda choice: (
                choice.text == "Load data" and [
                lambda: LoadContext(
                    on_close=lambda *data: (
                    data and ctx.get_head().child.load(data[0])
                    or [prompt]
                    )
                )
                ] or choice.text == "Save data" and [
                lambda: SaveContext(
                    data=ctx.get_head().child.save(),
                    on_close=lambda: [prompt]
                )
                ] or choice.text == "Nothing" and [prompt]
            ))
            ] or choice.text == "Edit controls" and [
                lambda: ControlsContext(bg=True)
            ] or choice.text == "Change name" and [
                (name, "Hm? A name change?"),
                (name, "Awfully finnicky, aren't we?"),
                lambda: NameEntryContext(
                    char=ctx.party[0].core,
                    on_close=lambda name: (
                    name != ctx.party[0].core.name and (
                        ctx.party[0].core.rename(name),
                        (name, lambda: ("Oho! So your name is ", ctx.party[0].core.token(), ".")),
                        (name, ". . . . ."),
                        (name, "...Well, it's certainly something.")
                    ) or (
                        (name, "Oh, changed your mind?"),
                        (name, "Well, if we ever figure out our little identity crisis, you know where to find me.")
                    )
                    )
                )
            ] or choice.text == "Nothing" and []
        ))
    ]
