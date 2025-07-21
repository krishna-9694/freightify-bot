import json
from collections import defaultdict

class AdaptiveLearning:
    def __init__(self):
        self.feedback_file = "feedback_log.jsonl"
        self.learning_data = defaultdict(list)
    
    def analyze_feedback(self):
        """Analyze user feedback to improve agent performance"""
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry['feedback'] == 'thumbs_down':
                        self.learning_data['poor_queries'].append(entry['query'])
                        self.learning_data['poor_responses'].append(entry['response'])
        except FileNotFoundError:
            pass
        
        return self._generate_improvements()
    
    def _generate_improvements(self):
        """Generate improvement suggestions based on feedback"""
        improvements = []
        
        if len(self.learning_data['poor_queries']) > 5:
            improvements.append("Consider retraining on common query patterns")
        
        if len(self.learning_data['poor_responses']) > 3:
            improvements.append("Review document chunking strategy")
            
        return improvements
    
    def get_query_suggestions(self, query: str):
        """Suggest query improvements based on learning"""
        # Simple keyword enhancement
        if len(query.split()) < 3:
            return f"{query} process workflow steps"
        return query