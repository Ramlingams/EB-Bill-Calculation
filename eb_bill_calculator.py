#!/usr/bin/env python3
"""
EB Bill Calculator - Simple CLI application

This application calculates an electricity (EB) bill for a residential consumer
based on slab rates and additional charges.

Default sample slab rates (editable in this file):
 - 0-100 units      : ₹3.00 / unit
 - 101-200 units    : ₹4.50 / unit
 - 201-300 units    : ₹6.00 / unit
 - >300 units       : ₹8.00 / unit

Other defaults:
 - Fixed charge     : ₹50.00
 - Electricity duty  : 5% (applied on energy charges)
 - GST              : 5% (applied on subtotal after duty)

Usage:
  - Run: python eb_bill_calculator.py
  - Follow the prompts: enter units consumed and optionally adjust rates.

The script also exposes a `calculate_bill(units, slabs, fixed_charge, duty_pct, gst_pct)`
function which can be imported into other projects or used in unit tests.
"""

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Slab:
    upto: int  # upper limit for this slab in units (0 means no upper limit)
    rate: float  # rate per unit

def calculate_bill(units: float,
                   slabs: List[Slab],
                   fixed_charge: float = 50.0,
                   duty_pct: float = 5.0,
                   gst_pct: float = 5.0) -> dict:
    """
    Calculate EB bill breakdown.

    Args:
      units: energy consumed in units (kWh)
      slabs: ordered list of Slab objects. The last slab should have upto=0 to indicate no upper limit.
      fixed_charge: fixed monthly charge (currency units)
      duty_pct: electricity duty percentage applied on energy charges
      gst_pct: GST percentage applied on (energy + duty + fixed_charge) typically

    Returns:
      dict with a detailed breakdown and totals
    """
    remaining = units
    energy_charge = 0.0
    slab_details = []

    prev_limit = 0
    for slab in slabs:
        if slab.upto == 0:
            # unlimited slab - take all remaining
            units_in_slab = max(0, remaining)
        else:
            slab_capacity = slab.upto - prev_limit
            units_in_slab = max(0, min(remaining, slab_capacity))

        charge = units_in_slab * slab.rate
        slab_details.append({
            "slab_range": f"{prev_limit+1}-{slab.upto if slab.upto!=0 else 'above'}",
            "units": units_in_slab,
            "rate": slab.rate,
            "charge": round(charge, 2)
        })
        energy_charge += charge
        remaining -= units_in_slab
        prev_limit = slab.upto
        if remaining <= 0:
            break

    energy_charge = round(energy_charge, 2)
    duty = round((duty_pct/100.0) * energy_charge, 2)
    subtotal = round(energy_charge + duty + fixed_charge, 2)
    gst = round((gst_pct/100.0) * subtotal, 2)
    total_bill = round(subtotal + gst, 2)

    return {
        "units": units,
        "slab_details": slab_details,
        "energy_charge": energy_charge,
        "fixed_charge": round(fixed_charge, 2),
        "duty_pct": duty_pct,
        "duty": duty,
        "gst_pct": gst_pct,
        "gst": gst,
        "subtotal": subtotal,
        "total_bill": total_bill
    }

def print_breakdown(bill: dict):
    print("\n--- EB BILL BREAKDOWN ---")
    print(f"Units consumed: {bill['units']}")
    print("\nSlab details:")
    for s in bill['slab_details']:
        print(f"  {s['slab_range']:12} | Units: {s['units']:6} | Rate: ₹{s['rate']:6.2f} | Charge: ₹{s['charge']:7.2f}")
    print(f"\nEnergy charge : ₹{bill['energy_charge']:.2f}")
    print(f"Fixed charge  : ₹{bill['fixed_charge']:.2f}")
    print(f"Electricity duty ({bill['duty_pct']:.2f}%) : ₹{bill['duty']:.2f}")
    print(f"Subtotal      : ₹{bill['subtotal']:.2f}")
    print(f"GST ({bill['gst_pct']:.2f}%)      : ₹{bill['gst']:.2f}")
    print(f"Total payable : ₹{bill['total_bill']:.2f}")
    print("-------------------------\n")

def prompt_float(prompt_text: str, default: float = None) -> float:
    while True:
        try:
            raw = input(prompt_text)
            if raw.strip() == "" and default is not None:
                return float(default)
            val = float(raw)
            if val < 0:
                print("Please enter a non-negative number.")
                continue
            return val
        except ValueError:
            print("Enter a valid number (e.g., 123.45)")

def main():
    print("EB Bill Calculator (simple)")
    units = prompt_float("Enter units consumed (kWh): ")

    # Default slabs - you can change these interactively if you want
    print("\nDefault slab structure (example):")
    print("  1) 0-100 @ ₹3.00")
    print("  2) 101-200 @ ₹4.50")
    print("  3) 201-300 @ ₹6.00")
    print("  4) >300 @ ₹8.00")
    use_defaults = input("Use default slabs? (Y/n): ").strip().lower()
    if use_defaults in ('', 'y', 'yes'):
        slabs = [Slab(100, 3.0), Slab(200, 4.5), Slab(300, 6.0), Slab(0, 8.0)]
    else:
        slabs = []
        print("Enter slab upper limit and rate. For the last slab, enter upper limit as 0.")
        idx = 1
        prev = 0
        while True:
            upto = int(prompt_float(f" Slab {idx} upper limit (units, 0 for no limit): ", default=0))
            rate = prompt_float(f" Slab {idx} rate (₹ per unit): ", default=1.0)
            slabs.append(Slab(upto, rate))
            idx += 1
            if upto == 0:
                break

    fixed = prompt_float("Fixed charge (₹) [default 50]: ", default=50.0)
    duty = prompt_float("Electricity duty (%) [default 5]: ", default=5.0)
    gst = prompt_float("GST (%) [default 5]: ", default=5.0)

    bill = calculate_bill(units, slabs, fixed_charge=fixed, duty_pct=duty, gst_pct=gst)
    print_breakdown(bill)

if __name__ == "__main__":
    main()
    //verion 1
//version 2 update