from penguin_game import *
from collections import namedtuple

##
def evaluateIceberg(game, iceberg, penguinsToSend):
    try:
        if iceberg == game.get_bonus_iceberg():
            return evaluateBonus(game, iceberg)
    except:
        print("")

    enemyPenguins = penguinsGroupsOnTheWay(game.get_enemy_penguin_groups(), iceberg)
    penguinAmount = iceberg.penguin_amount - penguinsToSend
    flag = False
    if penguinAmount == 0:
        owner = 0
    elif iceberg in game.get_my_icebergs():
        owner = 1
    elif iceberg in game.get_enemy_icebergs():
        owner = -1
    else:
        owner = 0
        flag = True
    penguinAmount += abs(owner) * iceberg.penguins_per_turn

    turn = 1
    turnConquer = 0
    minP = penguinAmount
    myPenguins = penguinsGroupsOnTheWay(game.get_my_penguin_groups(), iceberg)
    penguins = sorted(enemyPenguins + myPenguins, key=lambda penguin_group: actualTurnsTillArrival(penguin_group))
    for pg in penguins:
        if owner:
            penguinAmount += (actualTurnsTillArrival(pg) - turn) * iceberg.penguins_per_turn
            turn = actualTurnsTillArrival(pg)
            if pg in myPenguins and owner == 1:
                penguinAmount += pg.penguin_amount

            elif pg in enemyPenguins and owner == 1:
                penguinAmount -= pg.penguin_amount
                if minP > penguinAmount:
                    minP = penguinAmount
                if penguinAmount == 0:
                    owner = 0
                    minP = 0
                if penguinAmount < 0:
                    penguinAmount *= -1
                    owner = -1
                    minP = 0
                if flag:
                    turnConquer = turn
                    flag = False

            elif pg in enemyPenguins and owner == -1:
                penguinAmount += pg.penguin_amount

            elif pg in myPenguins and owner == -1:
                penguinAmount -= pg.penguin_amount
                if penguinAmount == 0:
                    owner = 0
                if penguinAmount < 0:
                    penguinAmount *= -1
                    owner = 1

        else:
            turn = actualTurnsTillArrival(pg)
            penguinAmount -= pg.penguin_amount
            if penguinAmount < 0:
                penguinAmount = abs(penguinAmount)
                if pg in myPenguins:
                    owner = 1
                else:
                    owner = -1
                    if flag:
                        turnConquer = turn
                        flag = False
                    turn -= 1

    minP = max(minP - 1, 0)
    return Icberg_state(belongs=owner, amount=penguinAmount, turn=turn, turn_conquered=turnConquer, can_send=minP)

##
def evaluateBonus(game, iceberg):
    enemyPenguins = penguinsGroupsOnTheWay(game.get_enemy_penguin_groups(), iceberg)
    penguinAmount = iceberg.penguin_amount
    flag = False
    if penguinAmount == 0:
        owner = 0
    elif game.get_my_bonus_iceberg():
        owner = 1
    elif game.get_enemy_bonus_iceberg() and game.get_enemy_bonus_iceberg().owner == game.get_enemy():
        owner = -1
    else:
        owner = 0
        flag = True

    turn = 1
    turnConquer = 0
    myPenguins = penguinsGroupsOnTheWay(game.get_my_penguin_groups(), iceberg)
    penguins = sorted(enemyPenguins + myPenguins, key=lambda penguinsroup: actualTurnsTillArrival(penguinsroup))
    for penguinsroup in penguins:
        turn = actualTurnsTillArrival(penguinsroup)
        if owner:
            if penguinsroup in myPenguins and owner == 1:
                penguinAmount += penguinsroup.penguin_amount

            elif penguinsroup in enemyPenguins and owner == 1:
                penguinAmount -= penguinsroup.penguin_amount

                if penguinAmount == 0:
                    owner = 0
                if penguinAmount < 0:
                    penguinAmount *= -1
                    owner = -1

            elif penguinsroup in enemyPenguins and owner == -1:
                penguinAmount += penguinsroup.penguin_amount

            elif penguinsroup in myPenguins and owner == -1:
                penguinAmount -= penguinsroup.penguin_amount
                if penguinAmount == 0:
                    owner = 0
                if penguinAmount < 0:
                    penguinAmount *= -1
                    owner = 1

        else:
            penguinAmount -= penguinsroup.penguin_amount
            if penguinAmount < 0:
                penguinAmount = abs(penguinAmount)
                if penguinsroup in myPenguins:
                    owner = 1
                else:
                    owner = -1
                    if flag:
                        turnConquer = turn
                        flag = False

    return Icberg_state(belongs=owner, amount=penguinAmount, turn=turn, turn_conquered=turnConquer, can_send=0)

##
def penguinsGroupsOnTheWay(penguinsroup, destination):
    penguins = filter(lambda penguinsroup: penguinsroup.destination == destination, penguinsroup)
    penguins = sorted(penguins, key=lambda x: actualTurnsTillArrival(x))
    return penguins

##
def amountCanUse(game, ice):
    groupD = {}
    groups = [p for p in (game.get_enemy_penguin_groups() + game.get_my_penguin_groups()) if p.destination.equals(ice)]
    for g in groups:
        if g.turns_till_arrival not in groupD:
            groupD[g.turns_till_arrival] = []
        groupD[g.turns_till_arrival].append(g)

    amount = ice.penguin_amount
    state = 1

    last_dist = 0

    lowest = amount
    enemy_penguin_sent = False

    for turn in sorted(groupD.keys()):
        groups = groupD[turn]

        if len(groups) < 2:
            group = groups[0]
            if state != 0:
                turns_to_add = turn - last_dist
                amount += turns_to_add * ice.penguins_per_turn
            if state == 1:
                amount_sent = group.penguin_amount
                if group.owner.equals(game.get_enemy()):
                    enemy_penguin_sent = True
                    amount_sent *= -1
                amount += amount_sent
                if amount < 0:
                    amount *= -1
                    state = -1
                elif amount == 0:
                    state = 0

            elif state == -1:
                amount_sent = group.penguin_amount
                if group.owner.equals(game.get_myself):
                    amount_sent *= -1
                else:
                    enemy_penguin_sent = True
                amount += amount_sent
                if amount < 0:
                    amount *= -1
                    state = 1
                elif amount == 0:
                    state = 0
            else:
                amount = group.penguin_amount
                state = 1 if group.owner.equals(game.get_myself) else -1
        else:
            my_penguin_amount = 0
            enemy_penguin_amount = 0
            for g in groups:
                if g.owner.equals(game.get_myself):
                    my_penguin_amount += g.penguin_amount
                else:
                    enemy_penguin_amount += g.penguin_amount
            if enemy_penguin_amount > 0:
                enemy_penguin_sent = True

            if state == 0:
                dec_amount = min(my_penguin_amount, enemy_penguin_amount)
                my_penguin_amount -= dec_amount
                enemy_penguin_amount -= dec_amount
                if enemy_penguin_amount == 0:
                    if my_penguin_amount > 0:
                        amount = my_penguin_amount
                        state = 1
                    else:
                        amount = 0
                else:
                    if enemy_penguin_amount > 0:
                        amount = enemy_penguin_amount
                        state = -1
                    else:
                        amount = 0
            else:
                turns_to_add = turn - last_dist
                amount += turns_to_add * ice.penguins_per_turn
                if state == -1:
                    if my_penguin_amount > amount + enemy_penguin_amount:  # We won
                        amount = my_penguin_amount - (amount + enemy_penguin_amount)
                        state = 1
                    elif my_penguin_amount == amount + enemy_penguin_amount:
                        state = 0
                        amount = 0
                    else:
                        amount += enemy_penguin_amount - my_penguin_amount
                else:
                    if my_penguin_amount + amount > enemy_penguin_amount:
                        amount += my_penguin_amount - enemy_penguin_amount
                    elif my_penguin_amount + amount == enemy_penguin_amount:
                        state = 0
                        amount = 0
                    else:
                        amount = enemy_penguin_amount - (my_penguin_amount + amount)
                        state = -1
        last_dist = turn
        if state == 1:
            if amount < lowest:
                lowest = amount
        elif state == -1:
            if -amount < lowest:
                lowest = -amount

    if enemy_penguin_sent:
        return lowest - 1
    return lowest

##
def safeToUpgrade(game, iceberg):
    if not iceberg.can_upgrade():
        return False

    level = iceberg.level + 1
    enemyPenguins = penguinsGroupsOnTheWay(game.get_enemy_penguin_groups(), iceberg)
    penguinAmount = iceberg.penguin_amount - iceberg.upgrade_cost
    if len(game.get_my_icebergs()) == 1 and len(game.get_enemy_icebergs()) == 1:
        if averageDistance(iceberg, game.get_enemy_icebergs()) * level + penguinAmount < game.get_enemy_icebergs()[
            0].penguin_amount:
            return False

    turn = 1
    myPenguins = penguinsGroupsOnTheWay(game.get_my_penguin_groups(), iceberg)
    penguins = sorted(enemyPenguins + myPenguins, key=lambda penguinsroup: actualTurnsTillArrival(penguinsroup))
    for penguinsroup in penguins:
        penguinAmount += (actualTurnsTillArrival(penguinsroup) - turn) * level
        turn = actualTurnsTillArrival(penguinsroup)
        if penguinsroup in myPenguins:
            penguinAmount += penguinsroup.penguin_amount
        else:
            penguinAmount -= penguinsroup.penguin_amount
            if penguinAmount <= 0:
                return False
    return True

##
def sumOfPenguins(penguinsroup):
    numP = 0
    for pg in penguinsroup:
        numP += pg.penguin_amount
    return numP

##
def averageDistance(iceberg, icebergs):
    distance = 0
    if not icebergs:
        return 100000
    for i in icebergs:
        distance += i.get_turns_till_arrival(iceberg)
    distance = distance / len(icebergs)
    return distance

##
def actualTurnsTillArrival(penguinsroup):
    source = penguinsroup.source
    destination = penguinsroup.destination
    bridge = bridgeExists(source, destination)
    if not bridge:
        return penguinsroup.turns_till_arrival
    if bridge.duration >= penguinsroup.turns_till_arrival:
        return int(penguinsroup.turns_till_arrival // bridge.speed_multiplier)
    return int((penguinsroup.turns_till_arrival - bridge.duration) + (bridge.duration // bridge.speed_multiplier))

##
def bridgeExists(source, destination):
    for b in source.bridges:
        edgesOfBridge = b.get_edges()
        if edgesOfBridge[0].equals(destination) or edgesOfBridge[1].equals(destination):
            return b
    return None

##
def buildBridge(game, iceberg, notSafeIcebergs):
    if iceberg.penguin_amount < game.iceberg_bridge_cost:
        return False
    cost = game.iceberg_bridge_cost
    maxDuration = game.iceberg_max_bridge_duration
    for nsi in notSafeIcebergs:
        groups = []
        for mpg in game.get_my_penguin_groups():
            if mpg.source == iceberg and mpg.destination == nsi:
                groups.append(mpg)
        if groups:
            numP = sumOfPenguins(groups)
            if numP > cost * 3 and filter(lambda x: x.turns_till_arrival >= maxDuration - 2, groups):
                state = evaluateIceberg(game, nsi, 0)
                if state.belongs == -1 and filter(lambda x: x.turns_till_arrival > state.turn_conquered, groups):
                    if evaluateIceberg(game, iceberg, cost).belongs == 1:
                        iceberg.create_bridge(nsi)
                        return True
    return False

##
def calculate(game, availableIcebergs):
    distance = 0
    penguinsToSend = sum(list(map(lambda x: x[1], availableIcebergs[1])))
    if availableIcebergs[1]:
        distance = availableIcebergs[1][-1][0].get_turns_till_arrival(availableIcebergs[0])
    try:
        if availableIcebergs[0] == game.get_bonus_iceberg():
            return - penguinsToSend
        else:
            return calculateBonus(penguinsToSend, distance, game, help, availableIcebergs)
    except:
        print(" ")
    return calculateBonus(penguinsToSend, distance, game, availableIcebergs)

##
def calculateBonus(penguinsToSend, distance, game, availableIcebergs):
    owner = 0
    if availableIcebergs[0] in game.get_my_icebergs():
        owner = 1
    elif availableIcebergs[0] in game.get_enemy_icebergs():
        owner = -1
    return - penguinsToSend - distance + owner + averageDistance(availableIcebergs[0], game.get_enemy_icebergs())

##
def calculateNeutral(game, iceberg):
    value = 0
    enemyDistance = averageDistance(iceberg, game.get_enemy_icebergs())
    myDistance = averageDistance(iceberg, game.get_my_icebergs())
    analyzer = evaluateIceberg(game, iceberg, 0)
    if analyzer.belongs == 1:
        return -10000000
    penguinAmount = analyzer.amount
    level = iceberg.level
    if enemyDistance >= myDistance:
        enemyDistance = 0
    value += level * 20 + enemyDistance * 5 - penguinAmount - myDistance * 11
    return value
    
##
def shouldUpgrade(game, iceberg):
    safe = list(filter(lambda x: evaluateIceberg(game, x, 0).belongs == 1, game.get_all_icebergs()))
    unsafe = sorted(list(set(game.get_all_icebergs()) - set(safe)), key=lambda x: x.get_turns_till_arrival(iceberg))
    size = len(unsafe)
    if size >= 1:
        state = evaluateIceberg(game, unsafe[0], 0)
        if (iceberg.get_turns_till_arrival(unsafe[0]) * 2 + state.amount) + state.turn < iceberg.upgrade_cost:
            return False
    if size >= 2:
        state = evaluateIceberg(game, unsafe[1], 0)
        if (iceberg.get_turns_till_arrival(unsafe[1]) * 2 + state.amount) + state.turn < iceberg.upgrade_cost:
            return False
    return True

##
def survive(game, ice):
    ices = [i for i in game.get_my_icebergs() if i.unique_id != ice.unique_id]
    ices.sort(key=lambda i2: i2.get_turns_till_arrival(ice))
    eIces = list(game.get_enemy_icebergs())
    eIces.sort(key=lambda i2: i2.get_turns_till_arrival(ice))
    lowest = 10000
    for enemy in eIces:
        dist = enemy.get_turns_till_arrival(ice)
        total = ice.penguin_amount + (dist * ice.penguins_per_turn)
        for other in ices:
            if other.get_turns_till_arrival(ice) + 1 < dist:
                total += other.penguin_amount
        after = total - enemy.penguin_amount
        lowest = min(after, lowest)
    return lowest

##
def notSafeIcebergs(game, iceberg):
    if len(game.get_enemy_icebergs()) < 2 and averageDistance(iceberg, game.get_enemy_icebergs()) == 7 and (
            game.get_enemy_icebergs()[0].penguin_amount > iceberg.penguin_amount + 10):
        return True
    return False

##
def numPenguinsToSend(game, iceberg, safe):
    try:
        if iceberg == game.get_bonus_iceberg():
            return bonusNumPenguinsToSend(game, iceberg, safe)
    except:
        print("")
    safe = sorted(safe, key=lambda x: x[0].get_turns_till_arrival(iceberg))
    icebergState = evaluateIceberg(game, iceberg, 0)
    numberOfPenguinsToSend = icebergState.amount + 1
    turn = icebergState.turn
    turn_conquered = icebergState.turn_conquered
    if iceberg.owner == game.get_neutral() and turn_conquered:  #
        for s in safe:
            if s[0].get_turns_till_arrival(iceberg) <= icebergState.turn_conquered:
                safe.remove(s)
    bridge = False
    icebergToSend = []
    for s in safe:
        penguinAmount = evaluateIceberg(game, s[0], s[0].penguin_amount - s[1]).can_send - s[
            0].penguins_per_turn + 1
        penguinAmount = max(0, penguinAmount)
        numberOfPenguinsToSend = numberOfPenguinsToSend + max(0, iceberg.get_turns_till_arrival(
            s[0]) - turn) * iceberg.level * (icebergState.belongs == -1)
        enemyGroups = game.get_enemy_penguin_groups()
        for epg in game.get_enemy_penguin_groups():
            if epg.source != iceberg or epg.destination != s:
                enemyGroups.remove(epg)
        count = 0
        for i in enemyGroups:
            count += i.penguin_amount
        enemyPenguins = count
        numberOfPenguinsToSend += enemyPenguins
        penguinAmount = min(penguinAmount + enemyPenguins, s[1])
        turn = max(iceberg.get_turns_till_arrival(s[0]), turn)
        bridgeSpare = s[0].get_turns_till_arrival(iceberg) - turn_conquered  #
        bridgeSpare *= turn_conquered != 0  ####
        if penguinAmount > game.iceberg_bridge_cost and numberOfPenguinsToSend > game.iceberg_bridge_cost and bridgeSpare > 0 and bridgeSpare * iceberg.penguins_per_turn > game.iceberg_bridge_cost:
            #                       "  "
            bridge = True
        if penguinAmount >= numberOfPenguinsToSend:
            if (icebergState.belongs or iceberg.penguin_amount == 0):
                #            0
                numberOfPenguinsToSend = int((penguinAmount + numberOfPenguinsToSend) / 2)
            icebergToSend += [(s[0], numberOfPenguinsToSend, bridge)]
            return icebergToSend
        elif penguinAmount > 0:
            icebergToSend += [(s[0], penguinAmount, bridge)]
            numberOfPenguinsToSend -= penguinAmount
        if bridge and numberOfPenguinsToSend < 0.7 * min(numberOfPenguinsToSend - 1,
                                                         s[0].get_turns_till_arrival(iceberg) - turn_conquered,
                                                         game.iceberg_max_bridge_duration) * iceberg.penguins_per_turn:
            return icebergToSend
    if iceberg in game.get_my_icebergs():
        return icebergToSend
    enemyAndNeutral = game.get_enemy_icebergs() + game.get_neutral_icebergs()
    myIcebergs = game.get_my_icebergs()
    for en in enemyAndNeutral:
        if mineInTheFuture(game, en):
            myIcebergs.append(en)
    if iceberg in myIcebergs:
        return icebergToSend
    icebergToSend = []
    return icebergToSend

##
def sendToBonus(game, safeIcebergs):
    try:
        if game.get_bonus_iceberg():
            if evaluateBonus(game, game.get_bonus_iceberg()).belongs != 1:  #
                bonusIceberg = game.get_bonus_iceberg()
                send = (bonusIceberg, numPenguinsToSend(game, bonusIceberg, safeIcebergs))
                if send[1]:
                    if game.get_neutral_bonus_iceberg() != game.get_bonus_iceberg() or evaluateBonus(
                            game, send[0]).belongs or send[0].penguin_amount == 0:
                        for icebergTuple in send[1]:
                            if icebergTuple[2]:
                                print("build a bridge")  #########check
                                # safe_one[0].create_bridge(send[0])
                            icebergTuple[0].send_penguins(send[0], icebergTuple[1])
                            temp = (icebergTuple[0], True)
                            if temp not in safeIcebergs:
                                safeIcebergs.remove((icebergTuple[0], False))
                                safeIcebergs += [temp]

                            for i in range(len(safe)):
                                if safe[i][0] == icebergTuple[0]:
                                    safe[i] = (icebergTuple[0], safe[i][1] - icebergTuple[1] - (
                                            icebergTuple[2] == True) * game.iceberg_bridge_cost)
                                    break

                        safe = list(filter(
                            lambda x: evaluateIceberg(game, x[0], x[0].penguin_amount - x[1]).belongs == 1,
                            safe))
                        bonusIcebergs = filter(lambda x: x != send[0], bonusIcebergs)

                        availableIcebergs = []

                        for bonusIceberg in bonusIcebergs:
                            availableIcebergs += [(bonusIceberg, numPenguinsToSend(game, bonusIceberg, safe))]
                        availableIcebergs = filter(lambda x: x[1] != [], availableIcebergs)
                        availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x), reverse=True)
                    else:
                        bonusIcebergs = filter(lambda x: x != send[0], bonusIcebergs)
                        availableIcebergs = []
                        for bonusIceberg in bonusIcebergs:
                            availableIcebergs += [(bonusIceberg, numPenguinsToSend(game, bonusIceberg, safe))]
                        availableIcebergs = filter(lambda x: x[1] != [], availableIcebergs)
                        availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x), reverse=True)
        return safeIcebergs
    except:
        return safeIcebergs

##
def mineInTheFuture(game, iceberg):
    if len(game.get_enemy_icebergs()) > 2:
        return False
    myPenguinsGroup = penguinsGroupsOnTheWay(game.get_my_penguin_groups(), iceberg)
    if myPenguinsGroup:
        for pg in myPenguinsGroup:
            if actualTurnsTillArrival(pg) == 1:
                return True
    return False

def sumOfPenguinsToDestination(penguin_group, destination):
    penguins = sumOfPenguins(filter(lambda penguin_group: penguin_group.destination == destination, penguin_group))
    return penguins

def send(game, safeIcebergs):
    for s in safeIcebergs:
        if s[0].level == 1 and shouldUpgrade(game, s[0]):
            safeIcebergs.remove(s)
    for s in safeIcebergs:
        if notSafeIcebergs(game, s[0]):
            safeIcebergs.remove(s)

    safeIcebergs = list(map(lambda x: (x[0], x[0].penguin_amount), safeIcebergs))
    safeIcebergs = sendToBonus(game, safeIcebergs)

    safeIcebergs = protect(game, safeIcebergs)

    if len(game.get_my_icebergs()) >= 2:
        safeIcebergs = sendMine(game, safeIcebergs)

    safeIcebergs = sendToNeutral(game, safeIcebergs)

    neutral = game.get_neutral_icebergs()
    for n in neutral:
        if averageDistance(n, game.get_enemy_icebergs()) < averageDistance(n, game.get_my_icebergs()):
            neutral.remove(n)

    for n in neutral:
        if evaluateIceberg(game, n, 0).belongs == 1:
            neutral.remove(n)

    if neutral:
        return safeIcebergs

    safeIcebergs = sendToEnemy(game, safeIcebergs)

    return safeIcebergs

##
def sendMine(game, safeIcebergs):
    myIcebergs = game.get_my_icebergs()
    for mi in myIcebergs:
        if averageDistance(mi, game.get_my_icebergs()) < averageDistance(mi, game.get_my_icebergs()):
            myIcebergs.remove(mi)
    myIcebergs = sorted(myIcebergs, key=lambda x: averageDistance(x, game.get_enemy_icebergs()))
    if len(myIcebergs) <= 2:
        myIcebergs = myIcebergs[0:1]
    elif len(myIcebergs) <= 5:
        myIcebergs = myIcebergs[0:2]
    elif len(myIcebergs) <= 7:
        myIcebergs = myIcebergs[0:3]
    else:
        myIcebergs = myIcebergs[0:4]
    safe = safeIcebergs
    safeIcebergs = filter(lambda x: x[0] not in myIcebergs, safeIcebergs)
    for s in safeIcebergs:
        myIcebergs = sorted(myIcebergs, key=lambda x: evaluateBridge(x, s[0]))
        state = evaluateIceberg(game, s[0], 0)
        if state.can_send > 0:
            s[0].send_penguins(myIcebergs[0], state.can_send - s[0].penguins_per_turn)
    return list(set(safe) - set(safeIcebergs))

##
def protect(game, safeIcebergs):
    enemyAndNeutral = game.get_enemy_icebergs() + game.get_neutral_icebergs()
    mine = game.get_my_icebergs()
    for en in enemyAndNeutral:
        if mineInTheFuture(game, en):
            mine.append(en)
    mine = filter(
        lambda x: sumOfPenguinsToDestination(game.get_enemy_penguin_groups(), x) > 0 and evaluateIceberg(game,
                                                                                                         x,
                                                                                                         0).belongs != 1,
        mine)
    availableIcebergs = []
    for m in mine:
        availableIcebergs += [(m, numPenguinsToSend(game, m, safeIcebergs))]
    for a in availableIcebergs:
        if not a[1]:
            availableIcebergs.remove(a)
    availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x))
    availableIcebergs.reverse()
    while availableIcebergs:
        send = availableIcebergs[0]
        for safe in send[1]:
            safe[0].send_penguins(send[0], safe[1])
            iceberg = (safe[0], True)
            if iceberg not in safeIcebergs:
                safeIcebergs = filter(lambda x: x[0] != safe[0], safeIcebergs)
            for i in range(len(safeIcebergs)):
                if safeIcebergs[i][0] == safe[0]:
                    safeIcebergs[i] = (safe[0], safeIcebergs[i][1] - safe[1])
                    break
        for si in safeIcebergs:
            if evaluateIceberg(game, si[0], si[0].penguin_amount - si[1]).belongs != 1:
                safeIcebergs.remove(si)
        for m in mine:
            if m == send[0]:
                mine.remove(m)
        availableIcebergs = []
        for m in mine:
            availableIcebergs += [(m, numPenguinsToSend(game, m, safeIcebergs))]
        availableIcebergs = filter(lambda x: x[1] != [], availableIcebergs)
        availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x), reverse=True)
    return safeIcebergs

##
def sendToEnemy(game, safeIcebergs):
    enemy = game.get_enemy_icebergs()
    closeToEnemy = safeIcebergs
    closeToEnemy = filter(
        lambda x: averageDistance(x[0], game.get_enemy_icebergs()) < averageDistance(x[0], game.get_my_icebergs()),
        safeIcebergs)
    closeToEnemy = sorted(closeToEnemy, key=lambda x: averageDistance(x[0], game.get_enemy_icebergs()))
    if len(closeToEnemy) >= 1:
        safeIcebergs.remove(closeToEnemy[0])

    availableIcebergs = []
    safe = []
    for s in safeIcebergs:
        safe.append(s[0])
    enemy = sorted(enemy, key=lambda x: averageDistance(x, safe))

    for e in enemy:
        enemyList = [(e, numPenguinsToSend(game, e, safeIcebergs))]
        if enemyList[0][1]:
            availableIcebergs += enemyList
            break

    if availableIcebergs:
        send = availableIcebergs[0]
        for s in send[1]:
            s[0].send_penguins(send[0], s[1])
            closeToEnemy = (s[0], True)

    return []

##
def sendToNeutral(game, safeIcebergs):
    neutral = game.get_neutral_icebergs()
    for n in game.get_neutral_icebergs():
        if calculateNeutral(game, n) == -10000000:
            neutral.remove(n)

    neutral = sorted(neutral, key=lambda x: calculateNeutral(game, x))
    neutral.reverse()

    if len(neutral) >= 2:
        neutral = neutral[0:2]
        if calculateNeutral(game, neutral[0]) > calculateNeutral(game, neutral[1]) + 25:
            neutral = neutral[0:1]
        for n in neutral:
            if evaluateIceberg(game, n, 0).belongs == 1:
                neutral.remove(n)

    availableIcebergs = []

    for n in neutral:
        availableIcebergs += [(n, numPenguinsToSend(game, n, safeIcebergs))]
        for a in availableIcebergs:
            if not a[1]:
                availableIcebergs.remove(a)
        if availableIcebergs:
            availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x))
        availableIcebergs.reverse()

    while availableIcebergs:
        send = availableIcebergs[0]
        for s in send[1]:
            s[0].send_penguins(send[0], s[1])
            safe = (s[0], True)

            if safe not in safeIcebergs:
                safeIcebergs = filter(lambda x: x[0] != s[0], safeIcebergs)

            for i in range(len(safeIcebergs)):
                if safeIcebergs[i][0] == s[0]:
                    safeIcebergs[i] = (s[0], safeIcebergs[i][1] - s[1])
                    break

                for si in safeIcebergs:
                    if evaluateIceberg(game, si[0], si[0].penguin_amount - si[1]).belongs != 1:
                        safeIcebergs.remove(si)
                for n in neutral:
                    if n == send[0]:
                        neutral.remove(n)
        availableIcebergs = []

        for n in neutral:
            availableIcebergs += [(n, numPenguinsToSend(game, n, safeIcebergs))]
        availableIcebergs = filter(lambda x: x[1] != [], availableIcebergs)
        availableIcebergs = sorted(availableIcebergs, key=lambda x: calculate(game, x))
        availableIcebergs.reverse()

    return safeIcebergs

##
def evaluateBridge(source, destination):
    duration = 0
    try:
        if source.bridges:
            bridge = source.bridges
            for b in source.bridges:
                if destination not in b.get_edges():
                    bridge.remove(b)
            if bridge:
                duration = bridge[0].duration
        elif destination.bridges:
            bridge = destination.bridges
            for b in destination.bridges:
                if source not in b.get_edges():
                    bridge.remove(b)
            if bridge:
                duration = bridge[0].duration
    except:
        print("")
    return source.get_turns_till_arrival(destination) - min(duration, int(
        source.get_turns_till_arrival(destination) + 1) / source.bridge_speed_multiplier)

Icberg_state = namedtuple("IcbergState", "belongs, amount, turn, turn_conquered, can_send")
ice_data = {}
def do_turn(game):
    for ice in game.get_my_icebergs():
        amount_to_use = amountCanUse(game, ice)
        safe_amount = survive(game, ice)
        amount_to_use = min(amount_to_use, safe_amount)
        info = {"can_use": amount_to_use, "can_act": True, "keep_from_dying": safe_amount}
        ice_data[ice.unique_id] = info
    if len(game.get_enemy_icebergs()) == 1 and len(game.get_my_icebergs()) >= 3:
        for mi in game.get_my_icebergs():
            cu = ice_data[mi.unique_id]["can_use"]
            if mi.penguin_amount >= 5:
                mi.send_penguins(game.get_enemy_icebergs()[0], cu)
        return
    
    if game.get_enemy_bonus_iceberg():
        if game.get_enemy_bonus_iceberg().penguin_amount==1:
            bonusSorted = sorted(game.get_my_icebergs(), key=lambda iceb: game.get_bonus_iceberg().get_turns_till_arrival(iceb))
            bonusSorted[0].send_penguins(game.get_bonus_iceberg(),2)
    #     
    safe = []
    for ice in game.get_my_icebergs():
        if evaluateIceberg(game, ice, 0).belongs == 1:
            safe.append(ice)
            
    #      
    if (not game.get_neutral_icebergs() and len(game.get_my_icebergs()) >= len(game.get_enemy_icebergs()) and safe == game.get_my_icebergs()) or len(safe) > len(game.get_enemy_icebergs()) and len(game.get_my_icebergs()) > 3:
        needsUpgrade = []
        for safeIce in safe:
            if safeIce.level != safeIce.upgrade_level_limit:
                needsUpgrade.append(safeIce)

        if needsUpgrade:
            sortedDistance = sorted(needsUpgrade, key=lambda x: averageDistance(x, game.get_enemy_icebergs()))
            safe = sortedDistance[:-1]
    
    #      
    for iceberg in list(set(game.get_my_icebergs()) - set(safe)):
        if safeToUpgrade(game, iceberg):
            iceberg.upgrade()

    #
    safeIcebergs = []
    for safeIceberg in safe:
        if safeToUpgrade(game, safeIceberg):
            safeIceberg.upgrade()
            safeIcebergs += [(safeIceberg, True)]
        else:
            safeIcebergs += [(safeIceberg, False)]
    
    #     
    for safeIceberg in safeIcebergs:
        if buildBridge(game, safeIceberg[0], list(set(game.get_all_icebergs()) - set(safe))):
            safeIcebergs.remove(safeIceberg)

    safeIcebergs = filter(lambda x: x[1] == False, send(game, filter(lambda x: x[1] == False, safeIcebergs)))