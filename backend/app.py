from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
# Enable CORS for vanilla JS frontend requests
CORS(app)

# In-Memory Database (Dummy Data)
projects = [
    {"id": "p1", "name": "Clean Water Initiative", "department": "Health", "allocated": 500000, "utilized": 150000, "output": 5000, "output_unit": "People Served"},
    {"id": "p2", "name": "Rural Education Expansion", "department": "Education", "allocated": 300000, "utilized": 280000, "output": 1200, "output_unit": "Students Enrolled"}
]

transactions = [
    {"id": "t1", "project_id": "p1", "amount": 50000, "category": "Infrastructure", "date": "2023-10-01", "desc": "Pipes & Filters"},
    {"id": "t2", "project_id": "p2", "amount": 280000, "category": "Contractors", "date": "2023-10-15", "desc": "School Building Setup"},
    {"id": "t3", "project_id": "p1", "amount": 100000, "category": "Logistics", "date": "2023-11-02", "desc": "Transport Vehicles"}
]

@app.route('/get_dashboard_data', methods=['GET'])
def get_dashboard_data():
    total_allocated = sum(p['allocated'] for p in projects)
    total_utilized = sum(p['utilized'] for p in projects)
    
    # Department-wise spending
    dept_spending = {}
    for p in projects:
        dept = p['department']
        dept_spending[dept] = dept_spending.get(dept, 0) + p['utilized']
        
    return jsonify({
        "total_allocated": total_allocated,
        "total_utilized": total_utilized,
        "balance": total_allocated - total_utilized,
        "dept_spending": dept_spending,
        "projects": projects
    })

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    # Enrich transactions with project names
    enriched_tx = []
    for tx in transactions:
        proj = next((p for p in projects if p['id'] == tx['project_id']), {})
        tx_copy = dict(tx)
        tx_copy['project_name'] = proj.get('name', 'Unknown')
        enriched_tx.append(tx_copy)
    return jsonify({"transactions": list(reversed(enriched_tx))})

@app.route('/add_project', methods=['POST'])
def add_project():
    data = request.json
    new_proj = {
        "id": f"p{len(projects)+1}",
        "name": data['name'],
        "department": data['department'],
        "allocated": float(data['allocated']),
        "utilized": 0,
        "output": 0,
        "output_unit": data.get('output_unit', 'Units')
    }
    projects.append(new_proj)
    return jsonify({"message": "Project added successfully", "project": new_proj})

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    amount = float(data['amount'])
    proj_id = data['project_id']
    
    new_tx = {
        "id": f"t{len(transactions)+1}-{uuid.uuid4().hex[:4]}",
        "project_id": proj_id,
        "amount": amount,
        "category": data['category'],
        "date": data.get('date', datetime.today().strftime('%Y-%m-%d')),
        "desc": data.get('desc', '')
    }
    transactions.append(new_tx)
    
    # Update utilized funds for the project
    for p in projects:
        if p['id'] == proj_id:
            p['utilized'] += amount
            
    return jsonify({"message": "Transaction logged successfully", "transaction": new_tx})

@app.route('/analyze', methods=['GET'])
def analyze_anomalies():
    alerts = []
    seen_amounts = {}
    
    for tx in transactions:
        # Rule 1: Spike Detection (Unusually high single transaction > $200k)
        if tx['amount'] > 200000:
            alerts.append(f"⚠️ High Spending Spike: ${tx['amount']} logged in Project '{tx['project_id']}' on {tx['date']}.")
            
        # Rule 2: Duplicate Detection (Same amount, same project, same category)
        key = f"{tx['project_id']}_{tx['amount']}_{tx['category']}"
        if key in seen_amounts:
            alerts.append(f"⚠️ Potential Duplicate: Repeated transaction of ${tx['amount']} for '{tx['category']}' in Project '{tx['project_id']}'.")
        seen_amounts[key] = True
        
        # Rule 3: Unauthorized category heuristic (Simulated AI)
        if tx['category'].lower() in ['entertainment', 'miscellaneous', 'unclassified']:
            alerts.append(f"⚠️ Policy Warning: Unauthorized or vague category '{tx['category']}' used for ${tx['amount']}.")

    if not alerts:
        alerts.append("✅ All transactions look normal. No anomalies detected.")
        
    return jsonify({"alerts": alerts})

@app.route('/impact_score', methods=['GET'])
def impact_score():
    impacts = []
    for p in projects:
        score = p['output'] / p['utilized'] if p['utilized'] > 0 else 0
        # Normalize score for demo (x1000 for readability)
        visual_score = score * 1000
        
        label = "Low"
        if visual_score > 15: label = "Medium"
        if visual_score > 30: label = "High"
        
        impacts.append({
            "project_name": p['name'],
            "score": round(visual_score, 2),
            "label": label,
            "metrics": f"{p['output']} {p['output_unit']} / ${p['utilized']}"
        })
    return jsonify({"impact_scores": impacts})

if __name__ == '__main__':
    app.run(debug=True, port=5000)