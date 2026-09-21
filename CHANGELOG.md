# Changelog

## V2.1.3 — 2026-05-30

### Fixed
- **PMC Number dropdown not populating** in Invoice, Payment, GST Release, Credit/Debit Note, and Hold Release modules — root cause was `GetDistinctPMCNoByContractorId` SP querying the empty legacy `invoice` table instead of `invoices`
- **Invoice module PMC field** changed from plain text input to a dropdown that auto-populates when a contractor is selected
- **Village Wise Advance column** repositioned in the filtered export Excel — now appears after Balance and before Status (was previously between GST SD Amount and hold columns)
- **"Failed to add state" error** — created missing `SaveStateWithStatus` stored procedure
- **State dropdown empty in Add District** — created missing `GetActiveStates` stored procedure

---

## V2.1.2 — 2026-05-29

### Fixed
- Renamed all DPR-type hold columns to **DPR Excess Amount** in output Excel and UI
- Fixed root cause where re-uploading an Excel would auto-create a new hold type with the original long DPR name instead of reusing the canonical "DPR Excess Amount" entry
- Removed "Download Full Report (Excel)" button from the contractor report page

### Added
- **Village Wise Advance** column in output Excel — reads the value from source Excel and stores it per invoice row; displayed as column 17 in the contractor report output

---

## V2.1.1 — 2026-05-28

### Fixed
- Hold amount mismatch: continuation rows with SD amount but no Invoice Details are now correctly captured via UPDATE after invoice insert
- Hold total formula now excludes DPR-type holds (`include_in_hold = 0`) matching the source Excel logic
- DPR hold column now shows gross amount instead of net (hold releases are already reflected in payments/surplus)

### Added
- `include_in_hold` flag on `hold_types` table — controls whether a custom hold type is included in the Hold total
- All DPR-type hold entries renamed to "DPR Excess Amount" in the database
- Duplicate UTR highlighting — rows with the same UTR number are highlighted orange in the output Excel
- Version badge updated from V2.1 to V2.1.1

---

## V2.1 — 2026-05-27

### Added
- Unified report service merging invoices and GST release rows in source Excel row order (`sort_order`)
- Credit / Debit Note support — stored in `credit_note` table, shown in output Excel grouped by PMC
- Hold Release support — stored in `hold_release` table
- Yellow separator rows between PMC sections in output Excel
- Summary section at the bottom of output Excel (Hold, Total Debit, Advance/Surplus, GST Remaining, custom hold breakdown)
- Auto-fit column widths in output Excel
- `GetHoldTypesByContractor` stored procedure returns `include_in_hold` field
