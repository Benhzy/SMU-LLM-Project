# ----- required imports -----

import json
import shutil
from pathlib import Path

# ----- execution code -----

shutil.copyfile('analysis_results.json', 'leaderboard/site/analysis_results.json')

with open('analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = sorted(
    data,
    key=lambda x: x.get('final_score', x.get('average_score', 0)),
    reverse=True
)

for idx, model in enumerate(models, 1):
    model['rank'] = idx

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LLM Leaderboard</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
</head>
<body>
    <div class="header-section">
        <h1>Leaderboard Overview</h1>
        <p>
            See how leading models stack up across legal reasoning, jurisdictional understanding, and more.<br>
            This leaderboard is updated automatically from <code>analysis_results.json</code>.
        </p>
        <button class="view-json-btn" onclick="window.open('analysis_results.json', '_blank')">
            View Raw analysis_results.json
        </button>
    </div>
    <div class="leaderboard-card">
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
    try:
        scores = model['final_synthesis']['evaluation']['scores']
        avg_score = model['final_synthesis']['evaluation']['average_score']
        assessment = model['final_synthesis']['evaluation']['overall_assessment']
        html_template += f"""
            <tr>
                <td>{model['rank']}</td>
                <td class="model-name">{model['model']}</td>
                <td>{scores.get('jurisdictional_understanding**', '')}</td>
                <td>{scores.get('legal_reasoning**', '')}</td>
                <td>{scores.get('comparative_analysis**', '')}</td>
                <td>{scores.get('practical_application**', '')}</td>
                <td>{avg_score}</td>
                <td class="overall-assessment">{assessment}</td>
                <td>{model.get('final_score', '')}</td>
            </tr>
        """
    except Exception as e:
        print(f"Skipping model {model.get('model', '')} due to error: {e}")

html_template += """
            </tbody>
        </table>
    </div>
    <script>
        $(document).ready(function() {
            $('#leaderboard').DataTable({
                "order": [[0, "asc"]],
                "paging": false,
                "info": false,
                "searching": true
            });
        });
    </script>
</body>
</html>
"""

Path('leaderboard/site').mkdir(parents=True, exist_ok=True)
with open('leaderboard/site/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)