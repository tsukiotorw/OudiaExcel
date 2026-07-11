## Domain Model Rules

- Railway is the root aggregate.
- Station belongs to Railway.
- Diagram belongs to Railway.
- Diagram owns Train.
- Train owns StopTime.
- StopTime references Station.
- Avoid reverse references unless explicitly required.
- Keep the domain model immutable where practical.
  