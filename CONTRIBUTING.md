# Contributing

Thank you for contributing to Pokemon Cardmarket Valuator.

## Principles

This project is based on strict, transparent, and reproducible pricing rules.

All contributions must respect:

- deterministic pricing logic
- explicit handling of uncertainty
- strict verification of Cardmarket pages
- no heuristic shortcuts on URLs
- no use of price guides or trend prices

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add or update tests
5. Open a Pull Request

## Pull Request Rules

A PR will be accepted only if:

- it respects all business rules in `PROJECT_SPEC.md`
- it does not weaken verification logic
- it does not introduce heuristic URL construction
- pricing logic remains deterministic
- fallback logic is explicit and documented
- tests are included for new logic

## Code Guidelines

- Keep modules small and focused
- Use type hints (Python / TypeScript)
- Avoid unnecessary abstractions
- Prefer clarity over cleverness
- Separate AI logic from deterministic logic

## Areas Where Contributions Are Welcome

- Card identification improvements
- Cardmarket page verification logic
- Listing parsing robustness
- Pricing engine improvements (within rules)
- UI/UX improvements
- Performance optimizations

## Areas That Require Extra Attention

- pricing_engine.py
- product_verification.py

Changes to these areas must include tests.

## Testing

At minimum, tests must cover:

- duplicate price removal
- average of first 5 distinct prices
- anomaly exclusion
- fallback behavior
- uncertain card handling

## Discussion First

For major changes, open an issue before coding.
