#!/usr/bin/env python3
"""Extract 1988 presidential results from the official FEC scanned PDF."""

from datetime import datetime, timezone
import difflib, hashlib, json, re
from pathlib import Path
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / "data" / "raw"; NORMALIZED = ROOT / "data" / "normalized"
PDF = "https://www.fec.gov/documents/1550/federalelections88.pdf"; LOCAL = ROOT / "tmp" / "pdfs" / "federalelections88.pdf"
STATE_MAP = {row["name"].upper(): row.get("abbr") for row in json.loads((NORMALIZED / "states.json").read_text())}
STATE_MAP.update({"DISTRICT OF COLUMBIA":"DC","VIRGIN ISLANDS":"VI","PUERTO RICO":"PR","GUAM":"GU","AMERICAN SAMOA":"AS"})


def main():
    RAW.mkdir(parents=True, exist_ok=True); NORMALIZED.mkdir(parents=True, exist_ok=True); rows=[]; state=None
    with pdfplumber.open(LOCAL) as pdf:
        for page in pdf.pages[9:30]:
            for raw in (page.extract_text() or "").splitlines():
                line=" ".join(raw.split()); upper=line.upper()
                if line and not any(ch.isdigit() for ch in line) and len(line)>3 and "," not in line and "CANDIDATE" not in upper and "PARTY" not in upper:
                    match=difflib.get_close_matches(upper, STATE_MAP, n=1, cutoff=.68)
                    if match: state=STATE_MAP[match[0]]; continue
                m=re.match(r"^(.*?)\s+([0-9][0-9,]*)\s+([0-9]+\.[0-9]+)$",line)
                if not state or not m or "TOTAL VOTE" in upper or line.lower().startswith("write-in"): continue
                label,votes,pct=m.groups(); label=label.strip()
                if not label or not any(ch.isalpha() for ch in label): continue
                key=f"1988|{state}|{label}"; rows.append({"fec_id":"LEGACY-"+hashlib.sha1(key.encode()).hexdigest()[:16].upper(),"candidate_label":label,"state":state,"votes":int(votes.replace(',','')),"vote_share":float(pct),"election_year":1988,"source":PDF,"source_page_range":"10-29","id_type":"synthetic legacy record ID"})
    rows=list({r["fec_id"]:r for r in rows}.values()); rows.sort(key=lambda r:(r["state"],-r["votes"],r["candidate_label"]))
    fn="fec_presidential_general_1988.json"; (NORMALIZED/fn).write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
    manifest={"retrieved_at":datetime.now(timezone.utc).isoformat(),"source":PDF,"format":"OCR text extracted from official PDF","records":len(rows),"file":"data/normalized/"+fn,"note":"OCR-distorted historical labels are preserved; stable synthetic IDs and source-page metadata are included."}
    (RAW/"fec_presidential_general_1988_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8"); print(json.dumps(manifest,indent=2))


if __name__ == "__main__": main()
