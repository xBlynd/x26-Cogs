"""
Defender - Protects your community with automod features and
           empowers the staff and users you trust with
           advanced moderation tools
Copyright (C) 2020  Twentysix (https://github.com/Twentysix26/)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import discord

async def make_status(ctx, cog, EmergencyModules, Action):
    pages = []
    guild = ctx.guild
    d_enabled = await cog.config.guild(guild).enabled()
    n_channel = guild.get_channel(await cog.config.guild(guild).notify_channel())
    can_sm_in_n_channel = None
    can_rm_in_n_channel = None
    if n_channel:
        can_sm_in_n_channel = n_channel.permissions_for(guild.me).send_messages
        can_rm_in_n_channel = n_channel.permissions_for(guild.me).read_messages

    n_role = guild.get_role(await cog.config.guild(guild).notify_role())
    can_ban = ctx.channel.permissions_for(guild.me).ban_members
    can_kick = ctx.channel.permissions_for(guild.me).kick_members
    can_read_al = ctx.channel.permissions_for(guild.me).view_audit_log

    msg = ("This is an overview of the status and the general settings.\n*Notify role* is the "
            "role that gets pinged in case of urgent matters.\n*Notify channel* is where I send "
            "notifications about reports and actions I take.\n\n")

    _not = "NOT " if not d_enabled else ""
    msg += f"Defender is **{_not}operational**.\n\n"

    p = ctx.prefix

    if not n_channel:
        msg += f"**Configuration issue:** Notify channel not set ({p}dset general notifychannel)\n"
    if can_sm_in_n_channel is False or can_rm_in_n_channel is False:
        msg += "**Configuration issue:** I cannot read and/or send messages in the notify channel.\n"
    if not n_role:
        msg += f"**Configuration issue:** Notify role not set ({p}dset general notifyrole)\n"
    if not can_ban:
        msg += "**Possible configuration issue:** I'm not able to ban in this server.\n"
    if not can_kick:
        msg += "**Possible configuration issue:** I'm not able to kick in this server.\n"
    if not can_read_al:
        msg += ("**Possible configuration issue:** I'm not able to see the audit log in this server. "
                "I may need this to detect staff activity.\n")
    if not d_enabled:
        msg += ("**Warning:** Since the Defender system is **off** every module will be shown as "
                "disabled, regardless of individual settings.\n")

    em = discord.Embed(color=discord.Colour.red(), description=msg)
    em.set_footer(text=f"`{p}dset general` to configure")
    em.set_author(name="Defender system")
    em.add_field(name="Notify role", value=n_role.mention if n_role else "None set", inline=True)
    em.add_field(name="Notify channel", value=n_channel.mention if n_channel else "None set", inline=True)

    pages.append(em)

    days = await cog.config.guild(guild).rank3_joined_days()

    msg = ("To grant you more granular control on *who* I should target "
            "and monitor I categorize the userbase in **ranks**.\n\n"
            "**Rank 1** are staff, trusted roles and helper roles\n**Rank 2** are "
            "regular users.\n**Rank 3** are users who joined this server "
            f"less than *{days} days ago*.\n")

    is_counting = await cog.config.guild(guild).count_messages()
    if is_counting:
        messages = await cog.config.guild(guild).rank3_min_messages()
        rank4_text = (f"**Rank 4** are users who joined less than *{days} days ago* "
                        f"and also have sent less than *{messages}* messages in this "
                        "server.\n\n")
    else:
        rank4_text = ("Currently there is no **Rank 4** because *message counting* "
                        "in this server is disabled.\n\n")

    msg += rank4_text

    msg += ("When setting the target rank of a module, that rank and anything below that will be "
            "targeted. Setting Rank 3 as a target, for example, means that Rank 3 and Rank 4 will be "
            "considered valid targets.\n\n")

    helpers = (f"**Helper roles** are users who are able to use `{p}alert` to report "
                "problems that need your attention.\nIf you wish, you can also enable "
                "*emergency mode*: if no staff activity is detected in a set time window "
                "after an *alert* is issued, helper roles will be granted access to modules "
                "that may help them in taking care of bad actors by themselves.\n")

    em_modules = await cog.config.guild(guild).emergency_modules()
    minutes = await cog.config.guild(guild).emergency_minutes()

    helpers += "Currently "
    if not em_modules:
        helpers += ("no modules are set to be available in *emergency mode* and as such it is disabled. "
                    "Some manual modules can be set to be used in *emergency mode* if you wish.\n\n")
    else:
        em_modules = [f"**{m}**" for m in em_modules]
        helpers += ("the modules " + ", ".join(em_modules))
        helpers += (f" will be available to helper roles after **{minutes} minutes** of staff inactivity "
                    "following an alert.\n\n")

    msg += helpers

    trusted = await cog.config.guild(guild).trusted_roles()
    helper = await cog.config.guild(guild).helper_roles()
    trusted_roles = []
    helper_roles = []

    for r in guild.roles:
        if r.id in trusted:
            trusted_roles.append(r.mention)
        if r.id in helper:
            helper_roles.append(r.mention)

    if not trusted_roles:
        trusted_roles = ["None set."]
    if not helper_roles:
        helper_roles = ["None set."]

    msg += "Trusted roles: " + " ".join(trusted_roles) + "\n"
    msg += "Helper roles: " + " ".join(helper_roles)

    em = discord.Embed(color=discord.Colour.red(), description=msg)
    em.set_footer(text=f"See `{p}dset rank3` `{p}dset general` `{p}dset emergency`")
    em.set_author(name="Ranks and helper roles")

    pages.append(em)

    enabled = False
    if d_enabled:
        enabled = await cog.config.guild(guild).raider_detection_enabled()

    rank = await cog.config.guild(guild).raider_detection_rank()
    messages = await cog.config.guild(guild).raider_detection_messages()
    minutes = await cog.config.guild(guild).raider_detection_minutes()
    action = await cog.config.guild(guild).raider_detection_action()
    wipe = await cog.config.guild(guild).raider_detection_wipe()

    msg = ("**Raider detection**\nThis auto-module is designed to counter raiders. It can detect large "
            "amounts of messages in a set time window and take action on the user.\n")
    msg += (f"It is set so that if a **Rank {rank}** user (or below) sends **{messages} messages** in "
            f"**{minutes} minutes** I will **{action}** them.\n")
    if Action(action) == Action.Ban and wipe:
        msg += f"The **ban** will also delete **{wipe} days** worth of messages.\n"
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    if d_enabled:
        enabled = await cog.config.guild(guild).invite_filter_enabled()
    rank = await cog.config.guild(guild).invite_filter_rank()
    action = await cog.config.guild(guild).invite_filter_action()
    action = f"**{action}** any user" if action != "none" else "**delete the message** of any user"
    msg += ("**Invite filter**\nThis auto-module is designed to take care of advertisers. It can detect "
            f"a standard Discord invite and take action on the user.\nIt is set so that I will {action} "
            f"who is **Rank {rank}** or below.\n")
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    if d_enabled:
        enabled = await cog.config.guild(guild).join_monitor_enabled()
    users = await cog.config.guild(guild).join_monitor_n_users()
    minutes = await cog.config.guild(guild).join_monitor_minutes()
    newhours = await cog.config.guild(guild).join_monitor_susp_hours()

    msg += ("**Join monitor**\nThis auto-module is designed to report suspicious user joins. It is able "
            "to detect an abnormal influx of new users and report any account that has been recently "
            "created.\n")
    msg += (f"It is set so that if **{users} users** join in the span of **{minutes} minutes** I will notify "
            "the staff with a ping.\n")
    if newhours:
        msg += f"I will also report any new user whose account is less than **{minutes} minutes old**.\n"
    else:
        msg += "Newly created accounts notifications are off.\n"
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    em = discord.Embed(color=discord.Colour.red(), description=msg)
    em.set_footer(text=f"`{p}dset raiderdetection` `{p}dset invitefilter` `{p}dset joinmonitor` to configure.")
    em.set_author(name="Auto modules")

    pages.append(em)

    if d_enabled:
        enabled = await cog.config.guild(guild).alert_enabled()
    em_modules = await cog.config.guild(guild).emergency_modules()
    minutes = await cog.config.guild(guild).emergency_minutes()

    msg = ("**Alert**\nThis manual module is designed to aid helper roles in reporting bad actors to "
            f"the staff. Upon issuing the `{p}alert` command the staff will get pinged in the set notification "
            "channel and will be given context from where the alert was issued.\nFurther, if any manual module is "
            "set to be used in case of staff inactivity (*emergency mode*), they will be rendered available to "
            "helper roles after the set time window.\n")
    if em_modules:
        msg += (f"It is set so that the modules **{', '.join(em_modules)}** will be rendered available to helper roles "
                f"after the staff has been inactive for **{minutes} minutes** following an alert.\n")
    else:
        msg += (f"No module is set to be used in *emergency mode*, therefore it cannot currently be triggered.\n")
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    if d_enabled:
        enabled = await cog.config.guild(guild).vaporize_enabled()

    msg += ("**Vaporize**\nThis manual module is designed to get rid of vast amounts of bad actors in a quick way "
            "without creating a mod-log entry. To prevent misuse only **Rank 3** and below are targetable by this "
            "module. This module can be rendered available to helper roles in *emergency mode*.\n")
    if EmergencyModules.Vaporize.value in em_modules:
        msg += "It is set to be rendered available to helper roles in *emergency mode*.\n"
    else:
        msg += "It is not set to be available in *emergency mode*.\n"
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    if d_enabled:
        enabled = await cog.config.guild(guild).silence_enabled()

    rank_silenced = await cog.config.guild(guild).silence_rank()

    msg += ("**Silence**\nThis manual module allows to enable auto-deletion of messages for the selected ranks.\n"
            "It can be rendered available to helper roles in *emergency mode*.\n")
    if rank_silenced:
        msg += (f"It is set to silence **Rank {rank_silenced}** and below.\n")
    else:
        msg += ("No rank is set to be silenced.\n")
    if EmergencyModules.Silence.value in em_modules:
        msg += "It is set to be rendered available to helper roles in *emergency mode*.\n"
    else:
        msg += "It is not set to be available in *emergency mode*.\n"
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    em = discord.Embed(color=discord.Colour.red(), description=msg)
    em.set_footer(text=f"`{p}dset alert` `{p}dset vaporize` `{p}dset silence` `{p}dset emergency` to configure.")
    em.set_author(name="Manual modules (1/2)")

    pages.append(em)

    if d_enabled:
        enabled = await cog.config.guild(guild).voteout_enabled()

    votes = await cog.config.guild(guild).voteout_votes()
    rank = await cog.config.guild(guild).voteout_rank()
    action = await cog.config.guild(guild).voteout_action()
    wipe = await cog.config.guild(guild).voteout_wipe()

    msg = ("**Voteout**\nThis manual module allows to start a voting session to expel a user from the "
           "server. It is most useful to helper roles, however staff can also use this.\n"
           "It can be rendered available to helper roles in *emergency mode*.\n")
    msg += (f"It is set so that **{votes} votes** (including the issuer) are required to **{action}** "
            f"the target user, which must be **Rank {rank}** or below.")
    if Action(action) == Action.Ban and wipe:
        msg += f"\nThe **ban** will also delete **{wipe} days** worth of messages."
    msg += "\n"
    if EmergencyModules.Voteout.value in em_modules:
        msg += "It is set to be rendered available to helper roles in *emergency mode*.\n"
    else:
        msg += "It is not set to be available in *emergency mode*.\n"
    msg += "This module is currently "
    msg += "**enabled**.\n\n" if enabled else "**disabled**.\n\n"

    em = discord.Embed(color=discord.Colour.red(), description=msg)
    em.set_footer(text=f"`{p}dset voteout` `{p}dset emergency` to configure.")
    em.set_author(name="Manual modules (2/2)")

    pages.append(em)

    return pages
