import lightbulb
import hikari
import miru
import os
import datetime
import checker

# Instantiate a Bot instance
bot = lightbulb.BotApp(token=os.getenv("TOKEN") or "", prefix="?", default_enabled_guilds=[986212119693389834, 1016890939245088861])
miru.install(bot)

# Prepare the list of found Arc invites and the final message
invite_list = []

class DeleteView(miru.View):
    @miru.button(label="Delete Invalid Invites", style=hikari.ButtonStyle.DANGER)
    async def delete_invites(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        delete_message = await ctx.message.respond("Deleting invalid invites...")
        invalid_invites = []
        for thrd, msg, invite, is_valid in invite_list:
            if not is_valid:
                invalid_invites.append("<" + invite + ">")
                await thrd.delete()
        await delete_message.edit(content="__Deleted invalid invites:__ - " + '\n - '.join(invalid_invites))


@bot.command
@lightbulb.command("ping", "Checks if the bot is alive")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    start_time = datetime.datetime.now()
    message = await ctx.respond("Pinging...")
    end_time = datetime.datetime.now()
    latency = round((end_time - start_time).total_seconds() * 1000, 3)
    await message.edit(content=f"Pong! Latency: {latency} ms")

@bot.command
@lightbulb.option("url", "The Arc invite URL to check", required=True)
@lightbulb.command("validate", "Determines if the given Arc invite is still valid")
@lightbulb.implements(lightbulb.SlashCommand)
async def check_url(ctx: lightbulb.SlashContext) -> None:
    message = await ctx.respond("Checking...")
    await message.edit(content="Valid invite!" if checker.check_is_valid_code(ctx.options.url) else "Invalid invite :(")

# TODO: Make this asynchronous somehow
@bot.command
@lightbulb.option("forum", "The forum to check", required=True, type=hikari.GuildChannel)
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.command("check_invites", "Iterates through all channels in a forum and checks Arc invites")
@lightbulb.implements(lightbulb.SlashCommand)
async def check_invites(ctx: lightbulb.SlashContext) -> None:
    # Start the initial response message
    final_message = await ctx.respond(f"Checking <#{ctx.options.forum.id}>...")

    # Iterate through all threads in the specified channel
    for thread in ctx.app.cache.get_threads_view_for_channel(ctx.guild_id, ctx.options.forum).values():
        # Iterate through all messages in each thread
        async for message in ctx.app.rest.fetch_messages(thread.id):
            content = message.content

            # Check if the message contains an Arc invite URL
            try:
                if "https://arc.net/gift/" in content:
                    # Extract the Arc invite URL
                    start_index = content.find("https://arc.net/gift/")
                    invite = content[start_index:].replace("\n", " ").split(" ")[0].replace(">", "")

                    # Check if the invite is valid
                    is_valid = checker.check_is_valid_code(invite)

                    # Append the invite details to the list
                    invite_list.append((thread, message, invite, is_valid))
            except Exception as e:
                pass

    # Prepare the final response message
    count = len(invite_list)
    if count == 0:
        response = "No Arc invites found."
    else:
        response = f"Found {count} Arc invites:\n"

    # Build the response message with formatted invite details
    for thrd, msg, invite, is_valid in invite_list:
        if is_valid:
            response += f"- <#{thrd.id}> - <{invite}> - Valid!\n"
        else:
            response += f"- <#{thrd.id}> - <{invite}> - Invalid :(\n"

    # Edit the initial response message with the final message content
    await final_message.edit(content=response)
    if "Invalid" in response:
        view = DeleteView(timeout=15)
        await final_message.edit(content=response + "\n\n**WARNING: There are invalid Arc invites in this forum. Should I delete them?**", components=view)
        await view.start(final_message)

print("THING: " + str(os.getenv("TOKEN")))
bot.run()

