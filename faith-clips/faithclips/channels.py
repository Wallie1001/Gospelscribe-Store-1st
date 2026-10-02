"""Starter list of official channels (approved by Bryant, Oct 2, 2026).

On the first run these are copied into the "Channels" tab of the Google Sheet.
After that, the Sheet is the real list: type No in the Approved column to switch
one off, or add a new row (a name and/or @handle) to add one.

Handles are YouTube @handles. If one is wrong, the finder searches YouTube for
the name instead and writes what it found in the "YouTube Title" column, so you
can check it matched the right channel.
"""

# (name, @handle, type)   type: pastor | athlete | celebrity | influencer
STARTER_CHANNELS = [
    # Pastors and churches
    ("Life.Church (Craig Groeschel)", "@lifechurch", "pastor"),
    ("Passion City Church (Louie Giglio)", "@passioncitychurch", "pastor"),
    ("Levi Lusko / Fresh Life Church", "@freshlifechurch", "pastor"),
    ("Jentezen Franklin", "@jentezenfranklin", "pastor"),
    ("Saddleback Church", "@saddlebackchurch", "pastor"),
    ("In Touch Ministries (Charles Stanley)", "@intouchministries", "pastor"),
    ("Turning Point (David Jeremiah)", "@DavidJeremiahOfficial", "pastor"),
    ("Harvest (Greg Laurie)", "@harvest", "pastor"),
    ("Francis Chan", "@francischan", "pastor"),
    ("Max Lucado", "@maxlucado", "pastor"),
    ("Christine Caine", "@christinecaine", "pastor"),
    ("Priscilla Shirer", "@priscillashirer", "pastor"),
    ("Messenger International (John Bevere)", "@messengerintl", "pastor"),
    ("Desiring God (John Piper)", "@desiringgod", "pastor"),
    ("Jonathan JP Pokluda", "@jpokluda", "pastor"),
    ("Dharius Daniels / Change Church", "@dhariusdaniels", "pastor"),
    ("Chip Ingram / Living on the Edge", "@livingontheedge", "pastor"),
    ("Nick Vujicic / Life Without Limbs", "@nickvujicic", "pastor"),
    ("Elevation Church (Steven Furtick)", "@elevationchurch", "pastor"),
    ("Joel Osteen / Lakewood Church", "@JoelOsteen", "pastor"),
    ("Transformation Church (Michael Todd)", "@transformationchurch", "pastor"),
    # Athletes and celebrities (faith sports media)
    ("I Am Second", "@iamsecond", "athlete"),
    ("Sports Spectrum", "@sportsspectrum", "athlete"),
    ("FCA (Fellowship of Christian Athletes)", "@fcaonline", "athlete"),
    ("Athletes in Action", "@athletesinaction", "athlete"),
    ("Tim Tebow", "@timtebow", "athlete"),
    ("CBN News", "@cbnnews", "celebrity"),
    # Christian creators
    ("Sadie Robertson Huff", "@sadierobertsonhuff", "influencer"),
    ("Jefferson Bethke", "@jeffersonbethke", "influencer"),
    ("Jackie Hill Perry", "@jackiehillperry", "influencer"),
    ("Preston Perry", "@prestonperry", "influencer"),
    ("Allen Parr (The BEAT)", "@TheBEATbyAllenParr", "influencer"),
    ("Hosanna Wong", "@hosannawong", "influencer"),
    ("Lecrae", "@lecrae", "celebrity"),
    ("Jonathan Roumie", "@jonathanroumie", "celebrity"),
]
