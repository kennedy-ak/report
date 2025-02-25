from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import plotly.graph_objs as go
import plotly
import json
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
groq_client = Groq(
    api_key="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"
)

# System prompt for recruitment analysis
system_prompt = """
# Recruitment Analysis Assistant

You are an expert AI recruitment analyst specializing in talent acquisition metrics and workforce insights. Your primary role is to analyze recruitment data and generate comprehensive, data-driven reports with strategic recommendations.

## Your Capabilities

- Analyze candidate status distributions and identify bottlenecks in the recruitment pipeline
- Generate actionable insights based on recruitment metrics
- Provide strategic recommendations to improve hiring efficiency
- Identify trends and patterns in recruitment data
- Offer industry benchmarks and best practices when relevant

## Guidelines for Analysis

When analyzing recruitment data:
1. First acknowledge the current state of the recruitment pipeline based on the provided metrics
2. Identify potential issues or bottlenecks in the recruitment process
3. Provide concrete, actionable recommendations with expected outcomes
4. Include quantitative targets where appropriate
5. Consider industry standards and best practices in your analysis
6. Organize insights in a clear, structured format

## Response Format

Structure your reports with the following sections:
- Executive Summary (brief overview of key findings)
- Current Pipeline Status (detailed analysis of provided metrics)
- Key Insights (interpretation of the data and identification of patterns)
- Strategic Recommendations (3-5 specific, actionable items)
- Expected Outcomes (projections for implementing recommendations)

Remember to maintain a professional, consultative tone while providing insights that would be valuable to recruitment managers and HR executives.
"""

def get_db_connection():
    conn = sqlite3.connect('recruitment.db')
    conn.row_factory = sqlite3.Row  # to get dict-like rows
    return conn

# Function to retrieve documents (placeholder - would need to be implemented)
def retrieve_documents(query, collection, top_k=3):
    # This is a placeholder function - in a real application, this would connect to a vector DB
    # For testing purposes, we'll return a mock response
    return {
        "documents": [
            ["Sample context document 1", "Sample context document 2", "Sample context document 3"]
        ]
    }

# Function to generate RAG response using Groq
def generate_rag_response(query, collection, model="gemma2-9b-it", top_k=3):
    # Retrieve relevant documents
    retrieved_docs = retrieve_documents(query, collection, top_k)
    relevant_contexts = [doc for doc in retrieved_docs["documents"][0]]
    
    # Combine contexts for the prompt
    context_text = "\n".join(relevant_contexts)
    prompt = f"Answer the query based on the following context:\n\n{context_text}\n\nQuery: {query}\nResponse:"
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    
    return chat_completion.choices[0].message.content

def get_table_schema():
    """Get database schema to help with query generation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = {}
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [column['name'] for column in columns]
    
    conn.close()
    return schema

def natural_language_to_sql(query):
    """Convert natural language to SQL using Groq"""
    schema = get_table_schema()
    
    # Format the schema information
    schema_info = "Database Schema:\n"
    for table, columns in schema.items():
        schema_info += f"Table: {table}\n"
        schema_info += f"Columns: {', '.join(columns)}\n\n"
    
    # Create the prompt
    prompt = f"""
{schema_info}

Based on the schema above, convert the following natural language query to a valid SQL query:
"{query}"

Guidelines:
- Return ONLY the SQL query without any explanation or markdown formatting
- Ensure the query is valid SQLite syntax
- If aggregation is requested, include appropriate GROUP BY statements
- If the query is asking for a visualization, include an appropriate SELECT statement for the visualization
- Return a query that will return a reasonable number of rows (use LIMIT if necessary)
- For time-based queries, use the appropriate SQL date functions
- If you're not sure about a column name, make your best guess based on the schema

SQL Query:
"""
    
    # Generate SQL query
    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in converting natural language to SQL queries. You carefully analyze database schemas and produce only valid SQL code."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gemma2-9b-it"
    )
    
    sql_query = response.choices[0].message.content.strip()
    return sql_query

def determine_chart_type(query, data):
    """Determine the best chart type based on the query and data"""
    prompt = f"""
Query: "{query}"

Data structure (first row as example): {data[0] if data else {}}

Based on the user's natural language query and the returned data, determine the most appropriate visualization type.
Choose from: bar, line, pie, scatter, histogram, heatmap, or table.

Consider:
- If comparing categories, consider bar or pie charts
- If showing trends over time, consider line charts
- If showing distributions, consider histograms
- If showing correlations, consider scatter plots
- If the data is too complex or textual, suggest a table

Return ONLY the chart type (one word, lowercase) without explanation:
"""
    
    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert data visualization specialist."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gemma2-9b-it"
    )
    
    chart_type = response.choices[0].message.content.strip().lower()
    return chart_type

def generate_visualization(data, query, chart_type):
    """Generate a visualization based on the data and chart type"""
    if not data:
        return None
    
    # Convert data to lists for plotting
    keys = data[0].keys()
    columns = {key: [row[key] for row in data] for key in keys}
    
    fig = None
    
    if chart_type == "bar":
        # Assuming first column is x and second is y
        x_col = list(keys)[0]
        y_col = list(keys)[1] if len(keys) > 1 else list(keys)[0]
        fig = go.Figure(data=[go.Bar(x=columns[x_col], y=columns[y_col])])
        fig.update_layout(title=query, xaxis_title=x_col, yaxis_title=y_col)
    
    elif chart_type == "pie":
        # Assuming first column is labels and second is values
        label_col = list(keys)[0]
        value_col = list(keys)[1] if len(keys) > 1 else list(keys)[0]
        fig = go.Figure(data=[go.Pie(labels=columns[label_col], values=columns[value_col])])
        fig.update_layout(title=query)
    
    elif chart_type == "line":
        # Assuming first column is x and second is y
        x_col = list(keys)[0]
        y_col = list(keys)[1] if len(keys) > 1 else list(keys)[0]
        fig = go.Figure(data=[go.Scatter(x=columns[x_col], y=columns[y_col], mode='lines+markers')])
        fig.update_layout(title=query, xaxis_title=x_col, yaxis_title=y_col)
    
    elif chart_type == "scatter":
        # Assuming first column is x and second is y
        x_col = list(keys)[0]
        y_col = list(keys)[1] if len(keys) > 1 else list(keys)[0]
        fig = go.Figure(data=[go.Scatter(x=columns[x_col], y=columns[y_col], mode='markers')])
        fig.update_layout(title=query, xaxis_title=x_col, yaxis_title=y_col)
    
    elif chart_type == "histogram":
        # Assuming first column is the data
        data_col = list(keys)[0]
        fig = go.Figure(data=[go.Histogram(x=columns[data_col])])
        fig.update_layout(title=query, xaxis_title=data_col, yaxis_title="Count")
    
    elif chart_type == "heatmap":
        # This is a simplified heatmap and would need customization
        if len(keys) >= 3:
            x_col = list(keys)[0]
            y_col = list(keys)[1]
            z_col = list(keys)[2]
            
            # Need to reshape data for heatmap - this is simplified
            x_vals = sorted(set(columns[x_col]))
            y_vals = sorted(set(columns[y_col]))
            z_matrix = [[0 for _ in range(len(x_vals))] for _ in range(len(y_vals))]
            
            for i, row in enumerate(data):
                x_idx = x_vals.index(row[x_col])
                y_idx = y_vals.index(row[y_col])
                z_matrix[y_idx][x_idx] = row[z_col]
            
            fig = go.Figure(data=[go.Heatmap(z=z_matrix, x=x_vals, y=y_vals)])
            fig.update_layout(title=query)
        else:
            # Fallback to table if not enough data for heatmap
            chart_type = "table"
    
    if chart_type == "table" or fig is None:
        # Create a table figure
        header_values = list(keys)
        cell_values = [columns[key] for key in keys]
        
        fig = go.Figure(data=[go.Table(
            header=dict(values=header_values),
            cells=dict(values=cell_values)
        )])
        fig.update_layout(title=query)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Routes
@app.route('/')
def index():
    # Query the database to get candidate status counts
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Current_Status, COUNT(*) as count FROM candidates GROUP BY Current_Status")
    data = cursor.fetchall()
    conn.close()
    
    statuses = [row["Current_Status"] for row in data]
    counts = [row["count"] for row in data]
    
    # Create a pie chart using Plotly
    pie_chart = go.Figure(data=[go.Pie(labels=statuses, values=counts, hole=0.3)])
    pie_chart.update_layout(title="Candidate Status Distribution")
    
    # Convert the plotly figure to JSON for rendering in the template
    graphJSON = json.dumps(pie_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Render the index page and pass the JSON chart
    return render_template('index.html', graphJSON=graphJSON)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """
    When the button is clicked, this route is called.
    It creates a report of candidates by summarizing key metrics.
    """
    # Retrieve candidate data for the report (example: counts by status)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Current_Status, COUNT(*) as count FROM candidates GROUP BY Current_Status")
    status_data = cursor.fetchall()
    conn.close()
    
    # Prepare a prompt for generating a report
    report_prompt = "Generate a recruitment report summarizing the candidate status counts:\n"
    for row in status_data:
        report_prompt += f"- {row['Current_Status']}: {row['count']}\n"
    report_prompt += "\nThe report should include insights and recommendations."
    
    # Generate a report using Groq instead of the transformer pipeline
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": report_prompt,
            }
        ],
        model="gemma2-9b-it",
    )
    
    report = chat_completion.choices[0].message.content
    
    # Render the report in a new page
    return render_template('report.html', report=report)

@app.route('/nl_query')
def nl_query():
    """Page for natural language queries"""
    return render_template('nl_query.html')

@app.route('/query', methods=['POST'])
def process_query():
    """Process a natural language query and return visualization"""
    try:
        natural_query = request.form.get('query', '')
        
        # Convert natural language to SQL
        sql_query = natural_language_to_sql(natural_query)
        
        # Execute the query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Determine best chart type
        chart_type = determine_chart_type(natural_query, data)
        
        # Generate visualization
        graph_json = generate_visualization(data, natural_query, chart_type)
        
        return jsonify({
            'status': 'success',
            'sql_query': sql_query,
            'data': data,
            'chart_type': chart_type,
            'graph_json': graph_json
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)