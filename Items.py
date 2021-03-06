"""


######################################
Item functions

Not yet a class...
######################################



"""
def doItems(cursor):
    items = writeItemFile(sortItemTables(getItemTables(cursor)), "itemData.lua")
    return items

def objectivesText(objectives):
    split = objectives.split('$B')
    temp = '\\n'.join(split)
    split1 = temp.split('$b')
    temp = '\\n'.join(split1)
    split2 = temp.split('$c')
    temp = '$C'.join(split2)
    split3 = temp.split('$r')
    temp = '$R'.join(split3)
    split4 = temp.split('$n')
    temp = '$N'.join(split4)
    return escapeName(temp)

def escapeName(string):
    name = string.replace('"', '\\"')
    name2 = name.replace("'", "\\'")
    return name2

def getItemTables(cursor):
    print("Selecting item related MySQL tables...")

    cursor.execute("SELECT entry, item, ChanceOrQuestChance, groupid, mincountOrRef FROM creature_loot_template")
    npc_loot_tpl = []
    for a in cursor.fetchall():
        npc_loot_tpl.append(a)

    cursor.execute("SELECT entry, item, ChanceOrQuestChance, groupid, mincountOrRef FROM gameobject_loot_template")
    obj_loot_tpl = []
    for a in cursor.fetchall():
        obj_loot_tpl.append(a)

    cursor.execute("SELECT entry, item, ChanceOrQuestChance, groupid, mincountOrRef FROM item_loot_template")
    item_loot_tpl = []
    for a in cursor.fetchall():
        item_loot_tpl.append(a)

    cursor.execute("SELECT entry, item, ChanceOrQuestChance, groupid, mincountOrRef FROM reference_loot_template")
    ref_loot_tpl = []
    for a in cursor.fetchall():
        ref_loot_tpl.append(a)

    cursor.execute("SELECT entry, name, Flags FROM item_template")
    item_tpl = []
    for a in cursor.fetchall():
        item_tpl.append(a)

    cursor.execute("SELECT entry, data1 FROM gameobject_template WHERE type = 3")
    obj_tpl = []
    for a in cursor.fetchall():
        obj_tpl.append(a)

    cursor.execute("SELECT entry, LootId, VendorTemplateId FROM creature_template") # PickpocketLootId and SkinningLootId might be good...
    npc_tpl = []
    for a in cursor.fetchall():
        npc_tpl.append(a)

    cursor.execute("SELECT entry, item, maxcount, incrtime FROM npc_vendor_template")
    npc_vendor_tpl = []
    for a in cursor.fetchall():
        npc_vendor_tpl.append(a)

    cursor.execute("SELECT entry, item, maxcount, incrtime FROM npc_vendor")
    npc_vendor = []
    for a in cursor.fetchall():
        npc_vendor.append(a)

    cursor.execute("SELECT entry, RewChoiceItemId1, RewChoiceItemId2, RewChoiceItemId3,RewChoiceItemId4 ,RewChoiceItemId5, RewChoiceItemId6, RewItemId1, RewItemId2, RewItemId3, RewItemId4 FROM quest_template")
    quest = []
    for a in cursor.fetchall():
        quest.append(a)

    cursor.execute("SELECT entry, name_loc3 FROM locales_item")
    item_loc_deDE = []
    for a in cursor.fetchall():
        item_loc_deDE.append(a)

    print("Done.")

    return [item_tpl, npc_loot_tpl, obj_loot_tpl, item_loot_tpl, ref_loot_tpl, npc_tpl, obj_tpl, npc_vendor_tpl, npc_vendor, quest, item_loc_deDE]

# entry, item, ChanceOrQuestChance, groupid, mincountOrRef
def getRefGroup(refLootTable, entry, chance):
    newTable = [] # (item, ChanceOrQuestChance)
    groupProcessed = [] # groupId
    for x in refLootTable:
        if x[0] == entry:
            if x[3] == 0:# not grouped
                # currently there are no other cases to cover here
                newTable.append((x[1], abs(x[2]*(chance/100))))
            else:# grouped
                if x[3] in groupProcessed:
                    continue
                else:
                    groupProcessed.append(x[3])
                    for y in getLootGroup(refLootTable, refLootTable, entry, x[3]):
                        newTable.append((y[0], abs(y[1]*(chance/100))))
    return newTable

def getLootGroup(lootTable, refLootTable, entry, groupId):
    newTable = []
    chance = 100
    for x in lootTable:
        if x[0] == entry and x[3] == groupId:
            if x[4] < 0:# reference
                for y in getRefGroup(refLootTable, abs(x[4]), abs(x[2])):
                    newTable.append(y)
            else:
                chance -= abs(x[2])
                newTable.append((x[1], abs(x[2])))
    newerTable = []
    numZeroChance = 0
    for x in newTable:
        if x[1] == 0:
            numZeroChance += 1
    if chance < 0:
        print("\nChance "+str(chance)+" for entry:"+str(entry)+", group: "+str(groupId)+", numZeroChance: "+str(numZeroChance))
    if numZeroChance > 0:
        newChance = chance/numZeroChance
    for x in newTable:
        if x[1] == 0:
            newerTable.append((x[0], newChance))
        else:
            newerTable.append(x)
    return newerTable

def getLootEntry(lootTable, refLootTable, entry):
    newTable = []
    groupProcessed = []
    for x in lootTable:
        if x[0] == entry:
            if x[3] == 0:# not grouped
                if x[4] > 0:# no reference
                    newTable.append((x[1], abs(x[2])))
                else: # reference
                    for y in getRefGroup(refLootTable, abs(x[4]), abs(x[2])):
                        newTable.append(y)
            else: # grouped
                if x[3] in groupProcessed:
                    continue
                else:
                    groupProcessed.append(x[3])
                    for y in getLootGroup(lootTable, refLootTable, entry, x[3]):
                        newTable.append(y)
    return newTable

def sortLootTable(lootTable, refLootTable):
    newTable = []
    processed = []
    count = len(lootTable)
    for x in lootTable:
        count -= 1
        if count % 5000 == 0:
            print(count, "...")
        if x[0] in processed:
            continue
        else:
            newTable.append([x[0], getLootEntry(lootTable, refLootTable, x[0]), []])
            processed.append(x[0])
    return newTable

def checkForItem(newLootTable, item):
    for x in newLootTable:
        if x[0] == item:
            return x[1]
    return False

def sortItemTables(itemTables):
    # entry, item, ChanceOrQuestChance, groupid, mincountOrRef
    """
    npcLootByGroup = {}
    for npc in itemTables[1]:
        npcLootByGroup[npc[0]] = npc
    npcLootByItem = {}
    for npc in itemTables[1]:
        if npc[1] is in npcLootByItem:
            npcLootByItem.append(npc)
        else:
            npcLootByItem[npc[1]] = [npc]
    objLootByGroup = {}
    for obj in itemTables[2]:
        objLootByGroup[obj[0]] = obj
    objLootByItem = {}
    for obj in itemTables[2]:
        if obj[1] is in objLootByItem:
            objLootByItem.append(obj)
        else:
            objLootByItem[obj[1]] = [obj]
    itmLootByGroup = {}
    for itm in itemTables[3]:
        itmLootByGroup[itm[0]] = itm
    itmLootByItem = {}
    for itm in itemTables[3]:
        if itm[1] is in itmLootByItem:
            itmLootByItem.append(itm)
        else:
            itmLootByItem[itm[1]] = [itm]
    refLootByGroup = {}
    for ref in itemTables[4]:
        refLootByGroup[ref[0]] = ref
    refLootByItem = {}
    for ref in itemTables[4]:
        if ref[1] is in refLootByItem:
            refLootByItem.append(ref)
        else:
            refLootByItem[ref[1]] = [ref]
    """

    print("Sorting NPC loot tables...")
    npcs = sortLootTable(itemTables[1], itemTables[4])
    print("Adding NPC ID's...")
    for x in npcs:
        for y in itemTables[5]:
            if y[1] == x[0]:
                x[2].append(y[0])
    print("Done.")

    print("Sorting Object loot tables...")
    objs = sortLootTable(itemTables[2], itemTables[4])
    print("Adding Object ID's...")
    for x in objs:
        for y in itemTables[6]:
            if y[1] == x[0]:
                x[2].append(y[0])
    print("Done.")

    print("Sorting Item loot tables...")
    items = sortLootTable(itemTables[3], itemTables[4])
    print("Done.")

    print("Sorting tables per item...")
    drops = []
    count = len(itemTables[0])
    for item in itemTables[0]:
        foundDrop = False
        newItem = [item[0], item[1], [], [], [], [], []]
        for npc in npcs:
            foundChance = checkForItem(npc[1], item[0])
            if foundChance:
                foundDrop = True
                for id in npc[2]:
                    newItem[2].append((id, foundChance))
        for obj in objs:
            foundChance = checkForItem(obj[1], item[0])
            if foundChance:
                foundDrop = True
                for id in obj[2]:
                    newItem[3].append((id, foundChance))
        for itm in items:
            for x in itm[1]:
                if x[0] == item[0]:
                    newItem[4].append((itm[0], x[1]))
                    foundDrop = True
        for itm in itemTables[8]:
            if itm[1] == item[0]:
                newItem[5].append((itm[0], itm[2], itm[3]))
                foundDrop = True
        for itm in itemTables[7]:
            if itm[1] == item[0]:
                for n in itemTables[5]:
                    if n[2] == itm[0]:
                        newItem[5].append((n[0], itm[2], itm[3]))
                        foundDrop = True
        for quest in itemTables[9]:
            for itm in quest[1:]:
                if itm == item[0]:
                    newItem[6].append(quest[0])
                    foundDrop = True
        if foundDrop:
            drops.append(newItem)
        count -= 1
        if count % 100 == 0:
            print(count, "...")
    print("Done.")
#[item_tpl, npc_loot_tpl, obj_loot_tpl, item_loot_tpl, ref_loot_tpl, npc_tpl, obj_tpl, npc_vendor_tpl, npc_vendor, quest, item_loc_deDE]
    return [drops, itemTables[10]]

def writeItemFile(itemData, locale = "enGB", file = "itemData.lua"):
    print("Printing item file...")
    items = itemData[0]
    if locale == "deDE":
        itemNames = {}
        for item in itemData[1]:
            itemNames[item[0]] = item[1]
        for item in items:
            if itemNames[item[0]] != '':
                item[1] = itemNames[item[0]]
    outfile = open(file, "w")

    outfile.write("itemLookup = {\n")
    for item in items:
        id = item[0]
        name = escapeName(item[1])
        outfile.write("\t['"+name+"'] = "+str(id)+",\n")
    outfile.write("}\n")

    outfile.write("itemData = {\n")
    for item in items:
        id = item[0]
        name = escapeName(item[1])
        outfile.write("\t["+str(id)+"] = {\n")

        outfile.write("\t\t{")
        for npc in item[2]:
            outfile.write("{"+str(npc[0])+","+str(round(abs(npc[1]), 2))+"},")
        outfile.write("},")

        outfile.write("{")
        for object in item[3]:
            outfile.write("{"+str(object[0])+","+str(round(abs(object[1]), 2))+"},")
        outfile.write("},")

        outfile.write("{")
        for itm in item[4]:
            outfile.write("{"+str(itm[0])+","+str(round(abs(itm[1]), 2))+"},")
        outfile.write("},")

        outfile.write("{")
        for itm in item[5]:
            if itm[1] > 0:
                outfile.write("{"+str(itm[0])+","+str(itm[1])+","+str(itm[2])+"},")
            else:
                outfile.write("{"+str(itm[0])+"},")
        outfile.write("},")

        outfile.write("{")
        for itm in item[6]:
            outfile.write(str(itm)+",")
        outfile.write("},\n")

        outfile.write("\t\t\""+name+"\",\n")

        outfile.write("\t},\n")
    outfile.write("}")
    print("Done.")

    return items
