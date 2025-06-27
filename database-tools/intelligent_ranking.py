#!/usr/bin/env python3
"""
🧠 Intelligent Solution Ranking & Machine Learning
Advanced ranking system for crash solutions using ML techniques

Features:
- Solution effectiveness prediction
- User feedback learning
- Context-aware ranking
- Success rate tracking
- Adaptive recommendations
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class IntelligentRanking:
    def __init__(self, db_path="vscode_issues_solutions.db"):
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.solution_vectors = None
        self.feedback_weights = {
            'success': 1.0,
            'partial_success': 0.6,
            'no_effect': 0.0,
            'made_worse': -0.5
        }
        self.context_weights = {
            'platform_match': 0.3,
            'version_match': 0.2,
            'severity_match': 0.2,
            'recency': 0.3
        }
        self.init_ml_components()
    
    def init_ml_components(self):
        """Initialize machine learning components"""
        try:
            # Create feedback tracking table
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solution_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solution_id INTEGER,
                    crash_context TEXT,
                    feedback_type TEXT,
                    effectiveness_score REAL,
                    user_comment TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (solution_id) REFERENCES solutions (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solution_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solution_id INTEGER,
                    crash_signature TEXT,
                    success_rate REAL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (solution_id) REFERENCES solutions (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Load or create solution vectors
            self.load_solution_vectors()
            
            print("✅ Intelligent ranking system initialized")
            
        except Exception as e:
            print(f"⚠️ ML initialization warning: {e}")
    
    def load_solution_vectors(self):
        """Load or create TF-IDF vectors for solutions"""
        vector_file = "solution_vectors.pkl"
        
        if os.path.exists(vector_file):
            try:
                with open(vector_file, 'rb') as f:
                    self.vectorizer, self.solution_vectors = pickle.load(f)
                print("📊 Loaded existing solution vectors")
                return
            except:
                pass
        
        # Create new vectors
        self.create_solution_vectors()
    
    def create_solution_vectors(self):
        """Create TF-IDF vectors for all solutions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.solution_title, s.solution_description, s.commands,
                   i.issue_type, i.error_signature, i.description
            FROM solutions s
            JOIN issues i ON s.issue_id = i.id
        ''')
        
        solutions = cursor.fetchall()
        conn.close()
        
        if not solutions:
            return
        
        # Combine text features for each solution
        solution_texts = []
        self.solution_ids = []
        
        for solution in solutions:
            text_features = [
                solution[1] or '',  # title
                solution[2] or '',  # description
                ' '.join(json.loads(solution[3]) if solution[3] else []),  # commands
                solution[4] or '',  # issue_type
                solution[5] or '',  # error_signature
                solution[6] or ''   # issue_description
            ]
            
            combined_text = ' '.join(text_features).lower()
            solution_texts.append(combined_text)
            self.solution_ids.append(solution[0])
        
        # Create TF-IDF vectors
        self.solution_vectors = self.vectorizer.fit_transform(solution_texts)
        
        # Save vectors
        try:
            with open("solution_vectors.pkl", 'wb') as f:
                pickle.dump((self.vectorizer, self.solution_vectors), f)
            print("💾 Solution vectors created and saved")
        except Exception as e:
            print(f"⚠️ Could not save vectors: {e}")
    
    def rank_solutions(self, solutions, crash_context, user_context=None):
        """Rank solutions using intelligent algorithms"""
        if not solutions:
            return solutions
        
        ranked_solutions = []
        
        for solution in solutions:
            score = self.calculate_solution_score(solution, crash_context, user_context)
            solution['intelligent_score'] = score
            ranked_solutions.append(solution)
        
        # Sort by intelligent score
        ranked_solutions.sort(key=lambda x: x['intelligent_score'], reverse=True)
        
        return ranked_solutions
    
    def calculate_solution_score(self, solution, crash_context, user_context=None):
        """Calculate comprehensive solution score"""
        base_score = solution.get('effectiveness_rating', 5) / 10.0
        
        # Semantic similarity score
        similarity_score = self.get_semantic_similarity(solution, crash_context)
        
        # Historical success rate
        success_score = self.get_historical_success_rate(solution, crash_context)
        
        # Context matching score
        context_score = self.get_context_matching_score(solution, user_context or {})
        
        # Recency and popularity score
        popularity_score = self.get_popularity_score(solution)
        
        # Verification bonus
        verification_bonus = 0.2 if solution.get('verified') else 0.0
        
        # Combine scores with weights
        final_score = (
            base_score * 0.3 +
            similarity_score * 0.25 +
            success_score * 0.25 +
            context_score * 0.15 +
            popularity_score * 0.05 +
            verification_bonus
        )
        
        return min(final_score, 1.0)  # Cap at 1.0
    
    def get_semantic_similarity(self, solution, crash_context):
        """Calculate semantic similarity between solution and crash context"""
        if not self.solution_vectors or not hasattr(self, 'solution_ids'):
            return 0.5  # Default score
        
        try:
            # Find solution index
            solution_title = solution.get('solution_title', '')
            solution_desc = solution.get('solution_description', '')
            
            # Create crash context vector
            crash_text = f"{crash_context} {solution_title} {solution_desc}".lower()
            crash_vector = self.vectorizer.transform([crash_text])
            
            # Calculate similarity with all solutions
            similarities = cosine_similarity(crash_vector, self.solution_vectors)
            max_similarity = np.max(similarities) if similarities.size > 0 else 0.5
            
            return float(max_similarity)
            
        except Exception as e:
            return 0.5  # Default score on error
    
    def get_historical_success_rate(self, solution, crash_context):
        """Get historical success rate for similar crashes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get solution ID (approximate match)
            solution_title = solution.get('solution_title', '')
            
            cursor.execute('''
                SELECT AVG(effectiveness_score), COUNT(*)
                FROM solution_feedback sf
                JOIN solutions s ON sf.solution_id = s.id
                WHERE s.solution_title LIKE ?
                AND sf.timestamp > datetime('now', '-30 days')
            ''', (f'%{solution_title[:20]}%',))
            
            result = cursor.fetchone()
            
            if result and result[0] is not None and result[1] > 0:
                avg_score = result[0]
                confidence = min(result[1] / 10.0, 1.0)  # More feedback = higher confidence
                return avg_score * confidence
            
            return 0.5  # Default score
            
        except Exception as e:
            return 0.5
        finally:
            conn.close()
    
    def get_context_matching_score(self, solution, user_context):
        """Calculate context matching score"""
        score = 0.0
        total_weight = 0.0
        
        # Platform matching
        solution_platform = solution.get('platform', '').lower()
        user_platform = user_context.get('platform', '').lower()
        
        if solution_platform and user_platform:
            if solution_platform == user_platform or solution_platform == 'all':
                score += self.context_weights['platform_match']
            total_weight += self.context_weights['platform_match']
        
        # Severity matching
        solution_severity = solution.get('severity', '').lower()
        crash_severity = user_context.get('severity', '').lower()
        
        if solution_severity and crash_severity:
            if solution_severity == crash_severity:
                score += self.context_weights['severity_match']
            elif (solution_severity in ['high', 'critical'] and 
                  crash_severity in ['high', 'critical']):
                score += self.context_weights['severity_match'] * 0.8
            total_weight += self.context_weights['severity_match']
        
        return score / total_weight if total_weight > 0 else 0.5
    
    def get_popularity_score(self, solution):
        """Calculate popularity score based on usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            solution_title = solution.get('solution_title', '')
            
            cursor.execute('''
                SELECT usage_count, success_rate
                FROM solution_usage su
                JOIN solutions s ON su.solution_id = s.id
                WHERE s.solution_title LIKE ?
                ORDER BY su.last_used DESC
                LIMIT 1
            ''', (f'%{solution_title[:20]}%',))
            
            result = cursor.fetchone()
            
            if result:
                usage_count, success_rate = result
                # Normalize usage count (log scale)
                usage_score = min(np.log(usage_count + 1) / 10.0, 1.0)
                success_rate = success_rate or 0.5
                
                return (usage_score * 0.3 + success_rate * 0.7)
            
            return 0.3  # Default for new solutions
            
        except Exception as e:
            return 0.3
        finally:
            conn.close()
    
    def record_solution_feedback(self, solution_id, crash_context, feedback_type, 
                                effectiveness_score, comment=""):
        """Record user feedback for solution effectiveness"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO solution_feedback 
                (solution_id, crash_context, feedback_type, effectiveness_score, user_comment)
                VALUES (?, ?, ?, ?, ?)
            ''', (solution_id, crash_context, feedback_type, effectiveness_score, comment))
            
            # Update usage statistics
            cursor.execute('''
                INSERT OR REPLACE INTO solution_usage 
                (solution_id, crash_signature, success_rate, usage_count, last_used)
                VALUES (
                    ?, 
                    ?, 
                    COALESCE((
                        SELECT (success_rate * usage_count + ?) / (usage_count + 1)
                        FROM solution_usage 
                        WHERE solution_id = ? AND crash_signature = ?
                    ), ?),
                    COALESCE((
                        SELECT usage_count + 1
                        FROM solution_usage 
                        WHERE solution_id = ? AND crash_signature = ?
                    ), 1),
                    datetime('now')
                )
            ''', (
                solution_id, crash_context[:100], effectiveness_score, 
                solution_id, crash_context[:100], effectiveness_score,
                solution_id, crash_context[:100]
            ))
            
            conn.commit()
            print(f"✅ Recorded feedback for solution {solution_id}")
            
        except Exception as e:
            print(f"⚠️ Error recording feedback: {e}")
        finally:
            conn.close()
    
    def get_learning_insights(self):
        """Get insights from machine learning analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Most effective solutions
            cursor.execute('''
                SELECT s.solution_title, AVG(sf.effectiveness_score) as avg_score,
                       COUNT(sf.id) as feedback_count
                FROM solutions s
                JOIN solution_feedback sf ON s.id = sf.solution_id
                WHERE sf.timestamp > datetime('now', '-30 days')
                GROUP BY s.id, s.solution_title
                HAVING feedback_count >= 3
                ORDER BY avg_score DESC
                LIMIT 5
            ''')
            
            top_solutions = cursor.fetchall()
            
            # Trending issues
            cursor.execute('''
                SELECT i.issue_type, COUNT(*) as frequency
                FROM issues i
                JOIN solutions s ON i.id = s.issue_id
                JOIN solution_feedback sf ON s.id = sf.solution_id
                WHERE sf.timestamp > datetime('now', '-7 days')
                GROUP BY i.issue_type
                ORDER BY frequency DESC
                LIMIT 5
            ''')
            
            trending_issues = cursor.fetchall()
            
            return {
                'top_solutions': [
                    {'title': row[0], 'score': round(row[1], 2), 'feedback_count': row[2]}
                    for row in top_solutions
                ],
                'trending_issues': [
                    {'issue_type': row[0], 'frequency': row[1]}
                    for row in trending_issues
                ],
                'total_feedback': self.get_total_feedback_count()
            }
            
        except Exception as e:
            print(f"⚠️ Error getting insights: {e}")
            return {'error': str(e)}
        finally:
            conn.close()
    
    def get_total_feedback_count(self):
        """Get total feedback count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM solution_feedback')
            return cursor.fetchone()[0]
        except:
            return 0
        finally:
            conn.close()

def main():
    """Test intelligent ranking system"""
    ranking = IntelligentRanking()
    
    # Test solution ranking
    test_solutions = [
        {
            'solution_title': 'Disable GPU Acceleration',
            'solution_description': 'Start VSCode without GPU acceleration',
            'effectiveness_rating': 8,
            'verified': True,
            'platform': 'linux',
            'severity': 'high'
        },
        {
            'solution_title': 'Clear Cache',
            'solution_description': 'Clear VSCode cache files',
            'effectiveness_rating': 6,
            'verified': False,
            'platform': 'all',
            'severity': 'medium'
        }
    ]
    
    crash_context = "ANOM_ABEND sig=11 code-insiders renderer crash"
    user_context = {'platform': 'linux', 'severity': 'high'}
    
    print("🧠 Testing intelligent ranking...")
    ranked = ranking.rank_solutions(test_solutions, crash_context, user_context)
    
    for i, solution in enumerate(ranked, 1):
        print(f"{i}. {solution['solution_title']}")
        print(f"   Score: {solution['intelligent_score']:.3f}")
        print(f"   Base Rating: {solution['effectiveness_rating']}/10")
        print()
    
    # Test feedback recording
    print("📝 Testing feedback recording...")
    ranking.record_solution_feedback(1, crash_context, 'success', 0.9, 'Worked perfectly!')
    
    # Get insights
    insights = ranking.get_learning_insights()
    print("📊 Learning Insights:")
    print(json.dumps(insights, indent=2))

if __name__ == '__main__':
    main()
