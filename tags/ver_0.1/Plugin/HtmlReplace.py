import re

def main(Entry):
    lRegGroup=[
			('>\s+<', '><'),                        
		]
    for sRegCell in lRegGroup:
        (sSource, sTarget) = sRegCell
        rInfo = re.compile(sSource)
        Entry = rInfo.sub(sTarget, Entry)
		
    return Entry
