from app.repositories.tier_repository import get_tier_has_available_room, get_distinct_max_guest, \
    get_num_available_room_by_id as siu, get_tier_name as gtn


def get_tiers(floor=None, max_guest=None):
    if floor and floor == 'all':
        floor = None
    if max_guest and max_guest == 'all':
        max_guest = None
    return get_tier_has_available_room(max_guest=max_guest, floor=floor)


def convert_get_tiers_to_dict(arr):
    result = []
    for a in arr:
        result.append({
            'ma': a[0],
            'name': a[1],
            'max_guest': a[2],
            'base_price': int(a[3]),
            'normal_guest_count': a[4],
            'extra_guest_surcharge': a[5],
            'foreign_guest_surcharge': a[6],
            'available': a[7],
            'surcharge': a[8]
        })
    return result


def tier_with_available_room_to_dict(tiers):
    serialized_tiers = []
    for row in tiers:
        tier_data = {
            'id': row[0],
            'name': row[1],
            'max_guest': row[2],
            'base_price': float(row[3]),
            'normal_guest_count': row[4],
            'extra_guest_surcharge': row[5],
            'foreign_guest_surcharge': row[6],
            'available': row[7],
            'surcharge': float(row[8])
        }
        serialized_tiers.append(tier_data)
    return serialized_tiers


def get_max_guests():
    return get_distinct_max_guest()


def get_num_available_room_by_id(id):
    return siu(id=id)


def get_tier_name(kw=None):
    tiers_names = gtn(kw=kw)
    return [] if tiers_names is None else tiers_names

