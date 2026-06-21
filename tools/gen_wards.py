#!/usr/bin/env python3
"""Generate js/wards/*.js ward boundary modules (approximate community estimates)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'js' / 'wards'
OUT.mkdir(parents=True, exist_ok=True)

MUMBAI_RAW = [
    ('A Ward — Colaba, Fort', 18.895, 19.020, 72.810, 72.840, 18.910, 72.825),
    ('B Ward — Dongri, Umarkhadi', 18.955, 19.035, 72.830, 72.855, 18.970, 72.842),
    ('C Ward — Bhuleshwar, Kalbadevi', 18.940, 19.050, 72.840, 72.870, 18.955, 72.850),
    ('D Ward — Malabar Hill, Tardeo', 18.960, 19.040, 72.790, 72.825, 18.970, 72.805),
    ('E Ward — Byculla, Mazgaon', 18.960, 19.060, 72.845, 72.875, 18.975, 72.860),
    ('F/N Ward — Sion, Matunga', 19.020, 19.070, 72.855, 72.895, 19.045, 72.870),
    ('F/S Ward — Parel, Sewri', 18.990, 19.040, 72.845, 72.875, 19.005, 72.860),
    ('G/N Ward — Dadar, Shivaji Park', 19.010, 19.045, 72.825, 72.855, 19.025, 72.840),
    ('G/S Ward — Worli, Lower Parel', 18.990, 19.030, 72.805, 72.835, 19.010, 72.820),
    ('H/E Ward — Bandra East, Khar East', 19.045, 19.085, 72.845, 72.885, 19.065, 72.865),
    ('H/W Ward — Bandra West, Khar West', 19.045, 19.095, 72.815, 72.855, 19.060, 72.835),
    ('K/E Ward — Andheri East, Vile Parle East', 19.095, 19.130, 72.845, 72.890, 19.115, 72.865),
    ('K/W Ward — Andheri West, Vile Parle West', 19.100, 19.145, 72.815, 72.855, 19.120, 72.835),
    ('L Ward — Kurla, Sakinaka', 19.065, 19.110, 72.870, 72.915, 19.090, 72.885),
    ('M/E Ward — Chembur, Deonar', 19.035, 19.075, 72.885, 72.925, 19.055, 72.905),
    ('M/W Ward — Marol, Jogeshwari', 19.105, 19.145, 72.855, 72.895, 19.125, 72.870),
    ('N Ward — Ghatkopar, Vikhroli', 19.085, 19.125, 72.895, 72.935, 19.100, 72.910),
    ('P/N Ward — Goregaon, Malad', 19.165, 19.205, 72.835, 72.875, 19.185, 72.855),
    ('P/S Ward — Kandivali, Charkop', 19.190, 19.225, 72.820, 72.860, 19.205, 72.840),
    ('R/N Ward — Dahisar, Borivali', 19.230, 19.270, 72.845, 72.885, 19.250, 72.865),
    ('R/C Ward — Borivali West', 19.220, 19.255, 72.830, 72.865, 19.235, 72.845),
    ('R/S Ward — Kandivali West', 19.200, 19.235, 72.810, 72.845, 19.215, 72.825),
    ('S Ward — Bhandup, Mulund', 19.145, 19.185, 72.915, 72.955, 19.165, 72.935),
    ('T Ward — Mulund, Nahur', 19.165, 19.205, 72.945, 72.985, 19.180, 72.960),
]

PUNE_AREAS = [
    'Kasba Vishrambag', 'Bhavani Peth', 'Swargate', 'Shaniwar Peth', 'Sadashiv Peth',
    'Kasba Peth', 'Narayan Peth', 'Raviwar Peth', 'Shukrawar Peth', 'Ganesh Peth',
    'Somwar Peth', 'Mangalwar Peth', 'Budhwar Peth', 'Shivajinagar', 'Model Colony',
    'Aundh', 'Baner', 'Balewadi', 'Pashan', 'Sus',
    'Kothrud', 'Karve Nagar', 'Warje', 'Dahanukar Colony', 'Bavdhan',
    'Erandwane', 'Deccan', 'Parvati', 'Dhankawadi', 'Bibwewadi',
    'Hadapsar', 'Magarpatta', 'Kondhwa', 'Mohammedwadi', 'Undri',
    'Wanowrie', 'Fatima Nagar', 'Koregaon Park', 'Kalyani Nagar', 'Yerwada',
    'Dhanori',
]

THANE_AREAS = [
    'Kopri', 'Naupada', 'Charai', 'Panchpakhadi', 'Vartak Nagar', 'Hiranandani Estate',
    'Ghodbunder Road', 'Kasarvadavali', 'Waghbil', 'Manpada', 'Bhayandarpada',
    'Majiwada', 'Kolshet', 'Balkum', 'Dhokali', 'Kalwa East', 'Kalwa West',
    'Mumbra', 'Diva', 'Shil',
    'Kausa', 'Rabodi', 'Jambli Naka', 'Temghar', 'Teen Hath Naka', 'Cadbury Junction',
    'Wagle Estate', 'Louis Wadi', 'Hari Niwas', 'Upvan', 'Yeoor Hills',
    'Patlipada', 'Hiranandani Meadows', 'Beverly Park', 'Vartak Nagar East', 'Oswal Park',
    'Kolshet Road', 'Mhada Colony', 'Indira Nagar', 'Ram Maruti Road', 'Shree Nagar',
    'Kisan Nagar', 'Naupada East', 'Talao Pali', 'Jambli Naka West', 'Kharegaon',
    'Kolshet Industrial', 'Balkum Naka', 'Dawodi', 'Kausa East', 'Mumbra Devi',
    'Diva East', 'Shil Phata', 'Kasheli', 'Bhiwandi Naka', 'Majiwada East',
    'Hiranandani Estate West', 'Manpada Hills', 'Bhayandarpada East', 'Waghbil Naka',
    'Ghodbunder Village', 'Kopri East', 'Charai West', 'Panchpakhadi North', 'Vartak Nagar West',
    'Kolshet West',
]


def fmt_ward(name, min_lat, max_lat, min_lng, max_lng, lat, lng):
    return {
        'name': name,
        'bbox': {
            'minLat': round(min_lat, 4),
            'maxLat': round(max_lat, 4),
            'minLng': round(min_lng, 4),
            'maxLng': round(max_lng, 4),
        },
        'centroid': {'lat': round(lat, 4), 'lng': round(lng, 4)},
    }


def grid_wards(prefix_fmt, areas, min_lat, max_lat, min_lng, max_lng, cols):
    wards = []
    lat_step = (max_lat - min_lat) / ((len(areas) + cols - 1) // cols)
    lng_step = (max_lng - min_lng) / cols
    rows = (len(areas) + cols - 1) // cols
    lat_step = (max_lat - min_lat) / rows
    for i, area in enumerate(areas):
        row, col = divmod(i, cols)
        wmin_lat = min_lat + row * lat_step
        wmax_lat = min_lat + (row + 1) * lat_step
        wmin_lng = min_lng + col * lng_step
        wmax_lng = min_lng + (col + 1) * lng_step
        clat = (wmin_lat + wmax_lat) / 2
        clng = (wmin_lng + wmax_lng) / 2
        wards.append(fmt_ward(prefix_fmt.format(n=i + 1, area=area), wmin_lat, wmax_lat, wmin_lng, wmax_lng, clat, clng))
    return wards


def write_js(filename, header, wards):
    lines = [header, 'export const WARDS = [']
    for w in wards:
        b = w['bbox']
        c = w['centroid']
        name = json.dumps(w['name'], ensure_ascii=False)
        lines.append(
            f"  {{ name: {name}, bbox: {{ minLat: {b['minLat']}, maxLat: {b['maxLat']}, "
            f"minLng: {b['minLng']}, maxLng: {b['maxLng']} }}, "
            f"centroid: {{ lat: {c['lat']}, lng: {c['lng']} }} }},"
        )
    lines.append('];')
    (OUT / filename).write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    mumbai = [fmt_ward(*w) for w in MUMBAI_RAW]
    pune = grid_wards('Ward {n} — {area}', PUNE_AREAS, 18.44, 18.58, 73.78, 73.95, 7)
    thane = grid_wards('TMC Ward {n} — {area}', THANE_AREAS, 19.15, 19.28, 72.92, 73.05, 9)

    write_js(
        'mumbai.js',
        """/**
 * Mumbai BMC wards — approximate community-tool bounding boxes.
 * NOT legal survey data. Names match CivicRadar datalist exactly.
 * Ref: MCGM ward map (mcgm.gov.in), OpenStreetMap Mumbai bounds.
 */""",
        mumbai,
    )
    write_js(
        'pune.js',
        """/**
 * Pune Municipal Corporation (PMC) electoral wards — ~41 wards.
 * Boundaries are approximate community grid estimates, NOT official survey data.
 * Ref: PMC ward list (pmc.gov.in), OpenStreetMap Pune city bounds.
 */""",
        pune,
    )
    write_js(
        'thane.js',
        """/**
 * Thane Municipal Corporation (TMC) electoral wards — ~65 wards.
 * Boundaries are approximate community grid estimates, NOT official survey data.
 * Ref: TMC ward list (thanecity.gov.in), OpenStreetMap Thane bounds.
 */""",
        thane,
    )
    print(f'Mumbai: {len(mumbai)}, Pune: {len(pune)}, Thane: {len(thane)}')


if __name__ == '__main__':
    main()
