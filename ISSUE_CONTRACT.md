# Issue Contract — `spacex-orbital-mechanics`

## Pain
Need correct LEO state / vis-viva / period for campaign and transfer planning.

## Claim
Kepler COE→state and vis-viva consistent for circular LEO.

## Proof
```bash
python3 job-app/helix/proofs/proof_orbital.py
```

## Done when
Proof exits 0. Architecture (strand/integrity/helix) is **not** a substitute for this proof.

## Anti-claim
Not a full flight dynamics suite.
