from dotenv import load_dotenv
import os
import json
import csv
from datetime import datetime
from collections import defaultdict
import ijson
import argparse


def parse_date(date_str):
    """Parse date string into datetime object."""
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip()

    if date_str.isdigit() and len(date_str) == 4:
        try:
            year = int(date_str)
            if 1900 <= year <= 2100:
                return datetime(year, 1, 1)
        except ValueError:
            pass

    # Formats à essayer dans l'ordre
    formats = [
        # Format ISO (avec ou sans timezone)
        lambda d: datetime.fromisoformat(d.replace('Z', '+00:00')) if 'T' in d else None,
        # Format standard YYYY-MM-DD
        lambda d: datetime.strptime(d, '%Y-%m-%d'),
        # Format en anglais: "Jan 5, 2004", "January 5, 2004"
        lambda d: datetime.strptime(d, '%b %d, %Y'),
        lambda d: datetime.strptime(d, '%B %d, %Y'),
        # Format sans virgule: "Jan 5 2004", "January 5 2004"
        lambda d: datetime.strptime(d, '%b %d %Y'),
        lambda d: datetime.strptime(d, '%B %d %Y'),
        # Format américain MM/DD/YYYY
        lambda d: datetime.strptime(d, '%m/%d/%Y'),
        # Format européen DD/MM/YYYY
        lambda d: datetime.strptime(d, '%d/%m/%Y'),
        # Format avec tirets DD-MM-YYYY
        lambda d: datetime.strptime(d, '%d-%m-%Y'),
    ]

    for format_parser in formats:
        try:
            date = format_parser(date_str)
            if not date:
                continue
            return date
        except (ValueError, TypeError):
            continue

    print(f"Attention: Impossible de parser la date: {date_str}")
    return None


def sort_json_by_year(input_file, output_directory, date_columns_name=None):
    """
    Trie les emplois par année depuis un fichier JSON via streaming.
    """
    os.makedirs(output_directory, exist_ok=True)
    filename_base = os.path.splitext(os.path.basename(input_file))[0]

    temp_files = {}
    job_counts = defaultdict(int)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            jobs = ijson.items(f, 'jobs.item')

            date_word = date_columns_name if date_columns_name else ['year', 'date', 'created', 'posted', 'publish']

            for job in jobs:
                date_field = None
                for date_term in date_word:
                    if date_term in job:
                        date_field = date_term
                        break
                if not date_field:
                    print(f"Attention: Impossible de trouver une colonne de date dans le fichier JSON {input_file}")
                    return {}

                date = parse_date(job[date_field])
                if date:
                    year = date.year
                    job_counts[year] += 1

                    if year not in temp_files:
                        temp_file_path = os.path.join(output_directory, f"{filename_base}_{year}_temp.json")
                        temp_files[year] = open(temp_file_path, 'w', encoding='utf-8')
                        temp_files[year].write('{"jobs": [')
                    else:
                        if job_counts[year] > 1:
                            temp_files[year].write(',')

                    json.dump(job, temp_files[year], ensure_ascii=False)

        for year, temp_file in temp_files.items():
            temp_file.write(']}')
            temp_file.close()

            temp_file_path = os.path.join(output_directory, f"{filename_base}_{year}_temp.json")
            final_file_path = os.path.join(output_directory, f"{filename_base}_{year}.json")

            with open(temp_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['nb_jobs'] = len(data['jobs'])
                data['year'] = year

            with open(final_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            os.remove(temp_file_path)

            print(f"Sauvegardé {job_counts[year]} emplois de {year} dans {final_file_path}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier JSON {input_file}: {e}")
        for temp_file in temp_files.values():
            temp_file.close()

    return dict(job_counts)


def sort_csv_by_year(input_file, output_directory, date_columns_name=None):
    """
    Trie les emplois par année depuis un fichier CSV via streaming.
    """
    print(output_directory)
    os.makedirs(output_directory, exist_ok=True)
    filename_base = os.path.splitext(os.path.basename(input_file))[0]

    csv_writers = {}
    csv_files = {}
    job_counts = defaultdict(int)

    try:
        with open(input_file, 'r', encoding='utf-8', newline='', errors='replace') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

            date_word = date_columns_name if date_columns_name else ['date', 'created', 'posted', 'publish']

            date_column_index = None
            for i, col_name in enumerate(header):
                if any(date_term in col_name.lower() for date_term in date_word):
                    date_column_index = i
                    print(f"Utilisation de la colonne '{col_name}' pour les informations de date")
                    break

            if date_column_index is None:
                print(f"Attention: Impossible de trouver une colonne de date dans le fichier CSV {input_file}")
                return {}

            for row in reader:
                if len(row) <= date_column_index:
                    continue

                date_str = row[date_column_index]
                date = parse_date(date_str)

                if date:
                    year = date.year
                    job_counts[year] += 1

                    if year not in csv_writers:
                        output_file = os.path.join(output_directory, f"{filename_base}_{year}.csv")
                        csv_files[year] = open(output_file, 'w', encoding='utf-8', newline='')
                        csv_writers[year] = csv.writer(csv_files[year], quoting=csv.QUOTE_MINIMAL)
                        csv_writers[year].writerow(header)

                    csv_writers[year].writerow(row)

        for f in csv_files.values():
            f.close()

        for year, count in job_counts.items():
            output_file = os.path.join(output_directory, f"{filename_base}_{year}.csv")
            print(f"Sauvegardé {count} emplois de {year} dans {output_file}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier CSV {input_file}: {e}")
        for f in csv_files.values():
            f.close()

    return dict(job_counts)


def process_directory(input_directory, output_directory, date_columns_name=None):
    """
    Traite tous les fichiers JSON et CSV dans un répertoire.
    """
    stats = {}

    for filename in os.listdir(input_directory):
        filepath = os.path.join(input_directory, filename)

        if os.path.isdir(filepath):
            continue

        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ['.json', '.csv']:
            continue

        print(f"Traitement de {filepath}...")

        if file_ext == '.json':
            result = sort_json_by_year(filepath, output_directory, date_columns_name)
        elif file_ext == '.csv':
            result = sort_csv_by_year(filepath, output_directory, date_columns_name)

        if result:
            stats[filename] = result

    print("\nRésumé:")
    for filename, year_counts in stats.items():
        print(f"  {filename}:")
        for year, count in sorted(year_counts.items()):
            print(f"    {year}: {count} emplois")


def process_single_file(input_file, output_directory, date_columns_name=None):
    """
    Traite un seul fichier (pour les très gros fichiers).
    """
    if not os.path.exists(input_file):
        print(f"Erreur: Le fichier {input_file} n'existe pas")
        return

    print(f"Traitement de {input_file}...")

    file_ext = os.path.splitext(input_file)[1].lower()
    if file_ext == '.json':
        sort_json_by_year(input_file, output_directory, date_columns_name)
    elif file_ext == '.csv':
        sort_csv_by_year(input_file, output_directory, date_columns_name)
    else:
        print(f"Format de fichier non supporté: {file_ext}")


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description='Trier les offres d\'emploi par année')
    parser.add_argument('--input', '-i', help='Fichier d\'entrée ou répertoire')
    parser.add_argument('--date_column-name', '-d', help='Nom de la colonne de date')
    parser.add_argument('--output', '-o', help='Répertoire de sortie')
    args = parser.parse_args()

    input_path = args.input or os.getenv("DIRECTORY_PATH")
    date_cols_name = args.date_column_name or os.getenv("DATE_COLUMN_NAME")
    if date_cols_name:
        date_cols_name = date_cols_name.split(',')
    else:
        date_cols_name = None
    output_dir = args.output or os.getenv("SORTED_DIRECTORY_PATH")

    print(f"Chemin d'entrée: {input_path}")
    print(f"Répertoire de sortie: {output_dir}")

    if os.path.isdir(input_path):
        process_directory(input_path, output_dir, date_cols_name)
    else:
        process_single_file(input_path, output_dir, date_cols_name)