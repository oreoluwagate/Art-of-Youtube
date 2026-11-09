# Week-5 "replay formula" pack (178-184): a quote/price -> Max calls it by ear/experience -> one-line payoff. 16-23s. Cast: Kevin, Max, Ben.
SH = []
def S(**k): SH.append(k)
G = lambda id, refs, p: dict(id=id, refs=refs, prompt=p)
KMB = lambda a='smug', b='deadpan', c='nervous': [('kevin', a), ('max', b), ('ben', c)]

S(n=178, title='THE DEALER SAID $3,800', set='desk', cast=KMB('talking', 'deadpan', 'nervous'),
  gag=G('g178', ['set_desk'], "Close-up on the shop's front counter: a printed car-dealership estimate sheet with a huge red handwritten total '$3,800' circled twice and the word 'TRANSMISSION' underlined, a car key with a fob lying on top of it."),
  beats=[
    ('L', 'ben', "[nervous] Dealer quoted her thirty-eight hundred. Says it's the transmission.", {'pose': 'nervous'}),
    ('S', 'click2', 0.0), ('H', 1.3, ('gag',)),
    ('L', 'kevin', "[panicked] That's the expensive one, right?", {'pose': 'panicked'}),
    ('S', 'whine', 0.0), ('H', 1.1, ('ms', 'max')),
    ('L', 'max', "[deadpan] Hear that whine? Fluid's low.", {'pose': 'deadpan'}),
    ('L', 'kevin', "So what does that cost?", {'pose': 'talking'}),
    ('L', 'max', "[dry] Eleven dollars. And a funnel.", {'pose': 'sideeye', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'kevin')),
  ])

S(n=179, title='SHE DID THE NOISE ON THE PHONE', set='desk', cast=KMB('talking', 'deadpan', 'excited'),
  gag=G('g179', ['set_repair'], "Close-up of a car's front tire with a big lumpy bulge where the tread belt has separated, comic wobble motion lines around the tire, cartoon 'WUB WUB WUB' sound-effect lettering floating next to it."),
  beats=[
    ('S', 'ring', 0.0), ('H', 0.5, ('ms', 'ben')),
    ('L', 'ben', "[on the phone, amused] She says it goes wub-wub-wub over forty.", {'pose': 'excited', 'shot': ('ms', 'ben')}),
    ('L', 'kevin', "[nervous] Could be anything. Bearing, axle, CV joint...", {'pose': 'talking'}),
    ('L', 'max', "[deadpan] Front tire. The belt's separating.", {'pose': 'deadpan'}),
    ('S', 'whoosh', 0.0), ('H', 1.3, ('gag',)),
    ('L', 'ben', "[amazed] From a phone call?", {'pose': 'panicked'}),
    ('L', 'max', "[dry] She does a very good wub.", {'pose': 'halfsmile', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'ben')),
  ])

S(n=180, title='THE NEIGHBOR SAID HEAD GASKET', set='lot', cast=KMB('panicked', 'deadpan', 'nervous'),
  gag=G('g180', ['set_lot'], "A car parked in the shop's parking lot on a frosty cold morning, frost on the windshield, a big harmless puff of white vapor drifting out of the tailpipe, cold breath-like clouds, early morning light."),
  beats=[
    ('L', 'kevin', "[panicked] Customer's neighbor says head gasket. Twenty-two hundred.", {'pose': 'panicked'}),
    ('S', 'whoosh', 0.0), ('H', 1.3, ('gag',)),
    ('L', 'max', "[deadpan] White smoke. How long?", {'pose': 'deadpan'}),
    ('L', 'ben', "Just a minute. When it's cold.", {'pose': 'nervous'}),
    ('L', 'max', "[deadpan] That's condensation. It's November.", {'pose': 'deadpan'}),
    ('L', 'kevin', "So the repair is...?", {'pose': 'talking'}),
    ('L', 'max', "[dry] Wait for spring.", {'pose': 'sideeye', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'kevin')),
  ])

S(n=181, title='$1,200 FOR BRAKES?', set='repair', cast=KMB('talking', 'deadpan', 'excited'),
  gag=G('g181', ['set_repair'], "Close-up of a car wheel up on the lift with the brake rotor and pads visible, and another shop's estimate taped to the tire that reads in big red letters '$1,200 - ROTORS, CALIPERS, EVERYTHING'."),
  beats=[
    ('L', 'ben', "[excited] Other shop quoted twelve hundred. Rotors, calipers, everything.", {'pose': 'excited'}),
    ('S', 'click2', 0.0), ('H', 1.2, ('gag',)),
    ('S', 'squeal', 0.0), ('H', 1.1, ('ms', 'max')),
    ('L', 'max', "[deadpan] That squeal's the wear tab. Pads only.", {'pose': 'deadpan'}),
    ('L', 'kevin', "Pads only? What's that cost?", {'pose': 'talking'}),
    ('L', 'max', "[deadpan] One-eighty.", {'pose': 'deadpan'}),
    ('L', 'ben', "[confused] Where'd the other thousand go?", {'pose': 'nervous'}),
    ('L', 'max', "[dry] Their boat.", {'pose': 'sideeye', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'max')),
  ])

S(n=182, title='THE $900 RATTLE', set='lot', cast=KMB('smug', 'deadpan', 'excited'),
  gag=G('g182', ['set_lot'], "View underneath a car in the parking lot: a loose shiny silver exhaust heat shield hanging by one bolt and rattling, with comic motion lines and 'RATTLE RATTLE' cartoon lettering."),
  beats=[
    ('L', 'kevin', "[proud] Customer looked it up. That rattle's a nine-hundred-dollar repair.", {'pose': 'smug'}),
    ('S', 'rattle', 0.0), ('H', 1.1, ('ms', 'max')),
    ('L', 'max', "[deadpan] Heat shield. It's loose.", {'pose': 'deadpan'}),
    ('S', 'whoosh', 0.0), ('H', 1.2, ('gag',)),
    ('L', 'ben', "[excited] Can we fix it today?", {'pose': 'excited'}),
    ('L', 'max', "[deadpan] Hose clamp. Two dollars.", {'pose': 'deadpan'}),
    ('L', 'kevin', "[panicked] What about the nine hundred?", {'pose': 'panicked'}),
    ('L', 'max', "[dry] Tell him to keep it.", {'pose': 'halfsmile', 'hold': 0.5}),
  ])

S(n=183, title='THE $5,000 CHECK ENGINE LIGHT', set='repair', cast=KMB('smug', 'deadpan', 'excited'),
  gag=G('g183', ['kevin', 'set_repair'], "Kevin (from the character reference) proudly holding up his phone next to a car dashboard with a glowing orange check-engine light; the phone screen shows a flashy estimate app reading 'ESTIMATE: $5,000' in huge red numbers."),
  beats=[
    ('L', 'kevin', "[proud] My app says this check engine light is a five-thousand-dollar repair.", {'pose': 'smug'}),
    ('H', 1.3, ('gag',)),
    ('L', 'max', "[deadpan] Gas cap's loose.", {'pose': 'deadpan'}),
    ('S', 'click2', 0.0), ('S', 'click2', 0.25), ('H', 0.7, ('ms', 'max')),
    ('L', 'ben', "[excited] Light's off!", {'pose': 'excited'}),
    ('L', 'kevin', "[defeated] The app was ninety-nine a month.", {'pose': 'defeated'}),
    ('L', 'max', "[dry] Gas cap was free.", {'pose': 'sideeye', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'kevin')),
  ])

S(n=184, title='DEALER WANTS A NEW ENGINE', set='repair', cast=KMB('talking', 'deadpan', 'nervous'),
  gag=G('g184', ['set_repair'], "Close-up of an open car engine bay with the oil dipstick pulled out and held up, the oil mark far below the 'ADD' line, almost dry, a comic sweat drop next to the engine."),
  beats=[
    ('L', 'ben', "[nervous] Dealer says it's knocking. Wants a new engine. Seven grand.", {'pose': 'nervous'}),
    ('S', 'tick', 0.0), ('H', 1.2, ('ms', 'max')),
    ('L', 'max', "[deadpan] That's not a knock. That's a tick.", {'pose': 'deadpan'}),
    ('S', 'click2', 0.0), ('H', 1.2, ('gag',)),
    ('L', 'max', "[deadpan] Two quarts low.", {'pose': 'deadpan', 'shot': ('gag',)}),
    ('L', 'kevin', "So the engine is...?", {'pose': 'talking'}),
    ('L', 'max', "[dry] Fine. Forty bucks of oil.", {'pose': 'sideeye', 'hold': 0.5}),
    ('H', 0.8, ('stare', 'kevin')),
  ])
