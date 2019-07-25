from spinn_machine.multicast_routing_entry import MulticastRoutingEntry


def chip_to_rules(chip_self, chip_pivot):
    if chip_pivot[0] == chip_self[0] and chip_pivot[1] == chip_self[1]:
        rule = 0
    elif chip_pivot[0] > chip_self[0] and chip_pivot[1] == chip_self[1]:
        rule = 1
    elif chip_pivot[0] < chip_self[0] and chip_pivot[1] == chip_self[1]:
        rule = 2
    elif chip_pivot[0] == chip_self[0] and chip_pivot[1] < chip_self[1]:
        rule = 3
    elif chip_pivot[0] == chip_self[0] and chip_pivot[1] > chip_self[1]:
        rule = 4
    elif chip_pivot[0] > chip_self[0] and chip_pivot[1] < chip_self[1]:
        rule = 5
    elif chip_pivot[0] > chip_self[0] and chip_pivot[1] > chip_self[1]:
        rule = 6
    elif chip_pivot[0] < chip_self[0] and chip_pivot[1] < chip_self[1]:
        rule = 7
    elif chip_pivot[0] < chip_self[0] and chip_pivot[1] > chip_self[1]:
        rule = 8
    else:
        raise Exception()
    
    return rule


class Router:
    def __init__(self):
        # SPIN2-MC Rules
        self._bc_rules = [list() for _ in range(9)]
        self._pp_rules = [list() for _ in range(9)]
        self._sync_rules = dict()

        self._rtr, _ = check_all()

        # Router CAM Entry
        self._bc_router = dict()
        self._pp_router = dict()
        self._sync_router = dict()

        for x in range(8):
            for y in range(8):
                if valid_chip(x, y):
                    self._bc_router[(x, y)] = list()
                    self._pp_router[(x, y)] = list()
                    self._sync_router[(x, y)] = list()

    def rules_init(self):
        cores = [core for core in range(1, 17)]

        # Broadcast
        for core in cores:
            bc_tmp = list(cores)
            bc_tmp.remove(core)
            self._bc_rules[0].append((bc_tmp, [0, 1, 2, 3, 4, 5]))
        self._bc_rules[1].append((cores, [2, 3, 4]))
        self._bc_rules[2].append((cores, [0, 1, 5]))
        self._bc_rules[3].append((cores, [1, 2]))
        self._bc_rules[4].append((cores, [4, 5]))
        self._bc_rules[5].append((cores, [2]))
        self._bc_rules[6].append((cores, [4]))
        self._bc_rules[7].append((cores, [1]))
        self._bc_rules[8].append((cores, [5]))

        # P2P
        for core in cores:
            self._pp_rules[0].append(([core], []))
        self._pp_rules[1].append(([], [0]))
        self._pp_rules[2].append(([], [3]))
        self._pp_rules[3].append(([], [5]))
        self._pp_rules[4].append(([], [2]))
        self._pp_rules[5].append(([], [5]))
        self._pp_rules[6].append(([], [1]))
        self._pp_rules[7].append(([], [4]))
        self._pp_rules[8].append(([], [3]))

    def get_rule(self, chip_self, chip_pivot, channel, processor_self):
        d = [[+1, 0], [+1, +1], [0, +1], [-1, 0], [-1, -1], [0, -1]]

        zone = chip_to_rules(chip_self, chip_pivot)

        if channel == "bc":
            rules = self._bc_rules[zone]
        elif channel == "pp":
            rules = self._pp_rules[zone]
        else:
            raise Exception

        if zone == 0:
            rule = rules[processor_self-1]
        else:
            rule = rules[0]

        true_external_rule = list()
        for direction in rule[1]:
            chip_dest = (chip_self[0] + d[direction][0], chip_self[1] + d[direction][1])
            if valid_chip(chip_dest[0], chip_dest[1]):
                true_external_rule.append(direction)

        return rule[0], true_external_rule

    def gen_rtr_stream(self):
        d = [[+1, 0], [+1, +1], [0, +1], [-1, 0], [-1, -1], [0, -1]]

        for chip in self._rtr.keys():

            sync1_key = "10000000000000000000000000000001"
            sync2_key = "10000000000000000000000000000010"
            sync3_key = "10000000000000000000000000000100"
            syncF_key = "10000000000000000000000000001000"
            sync_mask = "11111111111111111111111111111111"

            # SYNC 1 -> Core Collector Chip
            sync1_rule = ([1], [])
            self._sync_router[(chip[0], chip[1])].append((sync1_key, sync_mask, sync1_rule))

            # SYNC 2 -> Ring Collector Chip
            if chip[0] != chip[1]:
                if chip[0] > chip[1]:
                    sync2_rule = ([], [2])
                else:
                    sync2_rule = ([], [0])
            else:
                sync2_rule = ([1], [])
            self._sync_router[(chip[0], chip[1])].append((sync2_key, sync_mask, sync2_rule))

            # SYNC 3 -> Board Collector Chip
            if chip[0] == chip[1]:
                if chip[0] != 0:
                    sync3_rule = ([],[4])
                else:
                    sync3_rule = ([1],[])
                self._sync_router[(chip[0], chip[1])].append((sync3_key, sync_mask, sync3_rule))

            # SYNC Free -> Broadcast to Board
            syncF_rule = self.get_rule(chip, (0, 0), "bc", 1)
            self._sync_router[chip].append((syncF_key, sync_mask, syncF_rule))

            # BC
            for key in self._rtr[chip]:
                # Get Zone
                zone = int(key[2])
                rules = self._bc_rules[zone]

                for i, rule in enumerate(rules):
                    list_of_core = rule[0]
                    list_of_link = rule[1]

                    list_of_link_filtered = list()
                    for link in list_of_link:
                        chip_dest = (chip[0] + d[link][0], chip[1] + d[link][1])
                        if valid_chip(chip_dest[0], chip_dest[1]):
                            list_of_link_filtered.append(link)

                    rule_filtered = (list_of_core, list_of_link_filtered)

                    if zone == 0:
                        core = '{0:04b}'.format(i)
                        rtr_key = "01" + key[0] + core + "00000000000000000000"
                        rtr_msk = "11" + key[1] + "111100000000000000000000"
                    else:
                        rtr_key = "01" + key[0] + "000000000000000000000000"
                        rtr_msk = "11" + key[1] + "000000000000000000000000"

                    self._bc_router[(chip[0], chip[1])].append((rtr_key, rtr_msk, rule_filtered))

            # PP
            for key in self._rtr[chip]:
                # Get Zone
                zone = int(key[2])
                rules = self._pp_rules[zone]

                for i, rule in enumerate(rules):
                    list_of_core = rule[0]
                    list_of_link = rule[1]

                    list_of_link_filtered = list()
                    for link in list_of_link:
                        chip_dest = (chip[0] + d[link][0], chip[1] + d[link][1])
                        if valid_chip(chip_dest[0], chip_dest[1]):
                            list_of_link_filtered.append(link)

                    rule_filtered = (list_of_core, list_of_link_filtered)

                    if zone == 0:
                        core = '{0:04b}'.format(i)
                        rtr_key = "00" + key[0] + core + "00000000000000000000"
                        rtr_msk = "11" + key[1] + "111100000000000000000000"
                    else:
                        rtr_key = "00" + key[0] + "000000000000000000000000"
                        rtr_msk = "11" + key[1] + "000000000000000000000000"

                    self._pp_router[(chip[0], chip[1])].append((rtr_key, rtr_msk, rule_filtered))

    @property
    def bc_router(self):
        return dict(self._bc_router)

    @property
    def pp_router(self):
        return dict(self._pp_router)

    @property
    def sync_router(self):
        return dict(self._sync_router)

    @property
    def chips(self):
        return list(self._rtr.keys())

class Mask:
    def __init__(self, value):
        self._v = value
        self._n = len(self._v)
        self._x = self._v.count('X')
        self._p = next((self._n - i for i, e in enumerate(self._v) if e == 'X'), 0)

    @property
    def value(self):
        return self._v

    @property
    def x(self):
        return self._x

    @property
    def p(self):
        return self._p

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __cmp__(self, other):
        """ Compare by multiple rules """

        """ Order by: number of don't care """
        if self.x != other.x:
            return self.x - other.x

        """ Order by: position of first don't care """
        if self.p != other.p:
            return self.p - other.p

        """ Order by: bit values """
        if self.value < other.value:
            return -1
        elif self.value > other.value:
            return 1
        else:
            return 0


def key_rules_to_mask(l):
    if len(l) < 1:
        return []

    mask = [i for i in l[0]]
    for i in range(len(mask)):
        for e in l[1:]:
            if e[i] != mask[i]:
                mask[i] = 'X'
                break
    return mask


def mask_to_router_rules(mask, rule):
    m = ['0' if x == 'X' else '1' for x in mask]
    k = ['0' if x == 'X' else x for x in mask]
    return ''.join(k), ''.join(m), rule


def valid_chip(x, y):
    return 0 <= x < 8 and 0 <= y < 8 and x + 3 >= y >= x - 4


def router(router_rules, key):
    key = int(key, 2)
    for k, m, r in router_rules:
        k = int(k, 2)
        m = int(m, 2)
        if (key & m) == k:
            return r
    return -1


broadcast_rules = {0: [], 1: []}


def get_rules(self_x, self_y):
    router_rules = list()

    chip = (self_x, self_y)
    key_rules = {i: list() for i in range(9)}

    for x in range(8):
        for y in range(8):
            if valid_chip(x, y):
                key = "{:03b}{:03b}".format(x, y)
                rule = chip_to_rules(chip, (x, y))
                key_rules[rule].append(key)

    masks = {rule: key_rules_to_mask(key_rules[rule]) for rule in key_rules}
    sorted_masks = sorted(masks, key=lambda r: Mask(masks[r]))
    for rule in sorted_masks:
        if len(masks[rule]) > 0:
            k, m, r = mask_to_router_rules(masks[rule], rule)
            router_rules.append((k, m, r))

    return router_rules, key_rules


def check(x, y):
    if not valid_chip(x, y):
        raise Exception("Chip out of scope")

    fails = []
    router_rules, key_rules = get_rules(x, y)
    for expected_rule in key_rules:
        for key in key_rules[expected_rule]:
            rule = router(router_rules, key)
            if rule != expected_rule:
                fails.append("Expected rule {}, get {} for key {}".format(expected_rule, rule, key))
    assert len(fails) == 0, '\n'.join(fails)

    return router_rules, key_rules


def check_all(excludes=None):
    if excludes is None:
        excludes = []

    router = dict()
    keys = dict()

    errors = 0
    for x in range(8):
        for y in range(8):
            if valid_chip(x, y) and (x, y) not in excludes:
                try:
                    r, k = check(x, y)
                    router[(x, y)] = r
                    keys[(x, y)] = k
                except AssertionError as e:
                    print("FAIL {}:{}".format(x, y))
                    print(e)
                    errors += 1
    if errors == 0:
        print("VALID")

    return router, keys


def load_routing_keys(transceiver):
    rtr = Router()
    rtr.rules_init()
    rtr.gen_rtr_stream()

    routes_for_chip = list()

    for chip in rtr.sync_router.keys():
        routes_for_chip = list()
        for line in rtr.sync_router[chip]:
            routes_for_chip.append(
                MulticastRoutingEntry(int(line[0], 2),
                                      int(line[1], 2),
                                      line[2][0],
                                      line[2][1],
                                      False))
        transceiver.load_multicast_routes(chip[0], chip[1], routes_for_chip, 30)

    for chip in rtr.bc_router.keys():
        routes_for_chip = list()
        for line in rtr.bc_router[chip]:
            routes_for_chip.append(
                MulticastRoutingEntry(int(line[0], 2),
                                      int(line[1], 2),
                                      line[2][0],
                                      line[2][1],
                                      False))
        transceiver.load_multicast_routes(chip[0], chip[1], routes_for_chip, 30)

    for chip in rtr.pp_router.keys():
        routes_for_chip = list()
        for line in rtr.pp_router[chip]:
            routes_for_chip.append(
                MulticastRoutingEntry(int(line[0], 2),
                                      int(line[1], 2),
                                      line[2][0],
                                      line[2][1],
                                      False))
        transceiver.load_multicast_routes(chip[0], chip[1], routes_for_chip, 30)


