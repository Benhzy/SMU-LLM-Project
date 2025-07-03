# ----- required imports -----

import json
import shutil
from pathlib import Path


# ---- execution code ------

shutil.copyfile('analysis_results.json', 'leaderboard/site/analysis_results.json') # im just putting this here to guarantee access to raw json for now

with open('analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = sorted(
    data,
    key=lambda x: x.get('final_score', x.get('average_score', 0)),
    reverse=True
)

for idx, model in enumerate(models, 1):
    model['rank'] = idx

html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LLM Leaderboard</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
</head>
<body>
    <h1>LLM Leaderboard</h1>
    <button onclick="window.location.href='analysis_results.json'">View Raw analysis_results.json</button>
    <table id="leaderboard" class="display">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Model</th>
                <th>Jurisdictional Understanding</th>
                <th>Legal Reasoning</th>
                <th>Comparative Analysis</th>
                <th>Practical Application</th>
                <th>Average Score</th>
                <th>Overall Assessment</th>
                <th>Final Score</th>
            </tr>
        </thead>
        <tbody>
"""

for model in models:
    if model['final_synthesis']['evaluation']['scores']['jurisdictional_understanding'] is None:
        print(f"Error: {model['model']} has no jurisdictional understanding score")
        continue
    if model['final_synthesis']['evaluation']['scores']['legal_reasoning'] is None:
        print(f"Error: {model['model']} has no legal reasoning score")
        continue
    if model['final_synthesis']['evaluation']['scores']['comparative_analysis'] is None:
        print(f"Error: {model['model']} has no comparative analysis score")
        continue
    if model['final_synthesis']['evaluation']['scores']['practical_application'] is None:
        print(f"Error: {model['model']} has no practical application score")
        continue
    if model['final_synthesis']['average_score'] is None:
        print(f"Error: {model['model']} has no average score")
        continue
    print("All attributes detected for model:", model['model'])
    html_template += f"""
        <tr>
            <td>{model['rank']}</td>
            <td>{model['model']}</td>
            <td>{model['final_synthesis']['evaluation']['scores']['jurisdictional_understanding']}</td>
            <td>{model['final_synthesis']['evaluation']['scores']['legal_reasoning']}</td>
            <td>{model['final_synthesis']['evaluation']['scores']['comparative_analysis']}</td>
            <td>{model['final_synthesis']['evaluation']['scores']['practical_application']}</td>
            <td>{model['final_synthesis']['average_score']}</td>
            <td>{model['overall_assessment']}</td>
        </tr>
    """

html_template += """
        </tbody>
    </table>
    <script>
        $(document).ready(function() {
            $('#leaderboard').DataTable({
                "order": [[0, "asc"]]
            });
        });
    </script>
</body>
</html>
"""

Path('leaderboard/site').mkdir(parents=True, exist_ok=True)
with open('leaderboard/site/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
