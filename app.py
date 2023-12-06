from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch('http://localhost:9200')


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Extract form data
        game_title = request.form.get('game_title')
        topic = request.form.get('topic')
        review_content = request.form.get('review_content')
        sentiment = request.form.get('sentiment')
        # ... other filters ...

        # Construct Elasticsearch query with function score for custom ranking
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": [],
                            "should": [],
                            "filter": []
                        }
                    },
                    "functions": [
                        {
                            "field_value_factor": {
                                "field": "helpful",
                                "factor": 1.1,
                                "modifier": "log1p",
                                "missing": 0
                            }
                        },
                        {
                            "field_value_factor": {
                                "field": "hour_played",
                                "factor": 1.05,
                                "modifier": "log1p",
                                "missing": 0
                            }
                        },
                        # Add more functions as needed
                    ],
                    "boost_mode": "multiply"
                }
            },
            "sort": [
                {"_score": {"order": "desc"}}
            ]
        }

        # Add search terms to query if present
        if game_title:
            query['query']['function_score']['query']['bool']['must'].append(
                {"match": {"title": game_title}})
        if topic:
            query['query']['function_score']['query']['bool']['should'].append(
                {"match": {"Topic_Keywords": {"query": topic, "boost": 2}}})
        if review_content:
            query['query']['function_score']['query']['bool']['must'].append(
                {"match": {"review": review_content}})
        if sentiment:
            query['query']['function_score']['query']['bool']['filter'].append(
                {"term": {"sentiment": sentiment}})
        # ... add other conditions based on filters ...

        # Execute search query
        response = es.search(index="reviews", body=query)
        results = response['hits']['hits']

        return render_template('results.html', results=results)

    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
