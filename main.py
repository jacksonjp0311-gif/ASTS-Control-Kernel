import argparse

from engine.execution.runner import run_session


def main(argv=None):
    parser = argparse.ArgumentParser(description="ASTS Control Kernel")
    parser.add_argument(
        "--simulate",
        "--sim",
        action="store_true",
        help="labeled deterministic plant (SIMULATION MODE). Not a live process.",
    )
    parser.add_argument("--steps", type=int, default=10, help="session length (default 10)")
    args = parser.parse_args(argv)

    mode = "SIMULATION MODE" if args.simulate else "LIVE"
    print()
    print("ASTS Control Kernel")
    print("deterministic control for unstable loops")
    print(f"MODE  {mode}")
    print()
    run_session(steps=args.steps, simulate=args.simulate)


if __name__ == "__main__":
    main()
