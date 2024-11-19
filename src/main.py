from analyzer.dataset_analyzer import DatasetAnalyzer


def main():
    try:
        analyzer = DatasetAnalyzer("data/dataset.csv")
        analyzer.analyze()

    except FileNotFoundError:
        print("\nError: dataset.csv not found in current directory")
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    main()
