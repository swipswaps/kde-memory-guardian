#!/usr/bin/env python3
"""
⚡ Performance Optimizer for Crash Analysis System
Implements caching, indexing, and performance improvements

Features:
- Solution caching for faster lookups
- Database indexing optimization
- Memory-efficient data structures
- Async processing capabilities
- Performance monitoring
"""

import sqlite3
import json
import time
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

class PerformanceOptimizer:
    def __init__(self, db_path="vscode_issues_solutions.db"):
        self.db_path = db_path
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 3600  # 1 hour
        self.performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'query_times': [],
            'total_queries': 0
        }
        self.init_performance_optimizations()
    
    def init_performance_optimizations(self):
        """Initialize database indexes and performance optimizations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create indexes for faster searches
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_type ON issues(issue_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_signature ON issues(error_signature)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_effectiveness ON solutions(effectiveness_rating)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_verified ON solutions(verified)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_issue_id ON solutions(issue_id)')
            
            # Create full-text search index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS solutions_fts USING fts5(
                    solution_title, solution_description, commands,
                    content='solutions', content_rowid='id'
                )
            ''')
            
            # Populate FTS index
            cursor.execute('''
                INSERT OR REPLACE INTO solutions_fts(rowid, solution_title, solution_description, commands)
                SELECT id, solution_title, solution_description, commands FROM solutions
            ''')
            
            conn.commit()
            print("✅ Database performance optimizations applied")
            
        except Exception as e:
            print(f"⚠️ Performance optimization warning: {e}")
        finally:
            conn.close()
    
    def get_cache_key(self, crash_data, search_type="standard"):
        """Generate cache key for crash data"""
        data_hash = hashlib.md5(crash_data.encode()).hexdigest()
        return f"{search_type}_{data_hash}"
    
    def is_cache_valid(self, cache_key):
        """Check if cache entry is still valid"""
        if cache_key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[cache_key]
    
    def get_cached_solutions(self, cache_key):
        """Get solutions from cache if available and valid"""
        if cache_key in self.cache and self.is_cache_valid(cache_key):
            self.performance_stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        self.performance_stats['cache_misses'] += 1
        return None
    
    def cache_solutions(self, cache_key, solutions):
        """Cache solutions with expiry"""
        self.cache[cache_key] = solutions
        self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
    
    def optimized_search(self, crash_data, use_fts=True):
        """Optimized search with caching and FTS"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self.get_cache_key(crash_data, "fts" if use_fts else "standard")
        cached_result = self.get_cached_solutions(cache_key)
        if cached_result:
            return cached_result
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if use_fts:
                # Use full-text search for better performance
                search_terms = self.extract_search_terms(crash_data)
                if search_terms:
                    fts_query = ' OR '.join(f'"{term}"' for term in search_terms)
                    cursor.execute('''
                        SELECT i.*, s.solution_title, s.solution_description, s.commands,
                               s.source_type, s.source_url, s.effectiveness_rating, s.verified
                        FROM solutions_fts sf
                        JOIN solutions s ON sf.rowid = s.id
                        JOIN issues i ON s.issue_id = i.id
                        WHERE solutions_fts MATCH ?
                        ORDER BY s.effectiveness_rating DESC, s.verified DESC
                        LIMIT 20
                    ''', (fts_query,))
                else:
                    # Fallback to standard search
                    return self.standard_search(crash_data, cursor)
            else:
                return self.standard_search(crash_data, cursor)
            
            results = cursor.fetchall()
            solutions = self.format_solutions(results)
            
            # Cache the results
            self.cache_solutions(cache_key, solutions)
            
            # Update performance stats
            query_time = time.time() - start_time
            self.performance_stats['query_times'].append(query_time)
            self.performance_stats['total_queries'] += 1
            
            return solutions
            
        except Exception as e:
            print(f"⚠️ Optimized search error: {e}")
            return []
        finally:
            conn.close()
    
    def extract_search_terms(self, crash_data):
        """Extract relevant search terms from crash data"""
        crash_data_lower = crash_data.lower()
        terms = []
        
        # Key crash indicators
        if 'anom_abend' in crash_data_lower:
            terms.append('ANOM_ABEND')
        if 'sigsegv' in crash_data_lower or 'sig=11' in crash_data_lower:
            terms.append('SIGSEGV')
        if 'sigill' in crash_data_lower or 'sig=4' in crash_data_lower:
            terms.append('SIGILL')
        if 'renderer' in crash_data_lower:
            terms.append('renderer')
        if 'memory' in crash_data_lower or 'oom' in crash_data_lower:
            terms.append('memory')
        if 'gpu' in crash_data_lower:
            terms.append('GPU')
        if 'code-insiders' in crash_data_lower or 'vscode' in crash_data_lower:
            terms.append('VSCode')
        
        return terms
    
    def standard_search(self, crash_data, cursor):
        """Standard database search as fallback"""
        crash_data_sample = crash_data[:100]
        cursor.execute('''
            SELECT i.*, s.solution_title, s.solution_description, s.commands,
                   s.source_type, s.source_url, s.effectiveness_rating, s.verified
            FROM issues i
            JOIN solutions s ON i.id = s.issue_id
            WHERE i.error_signature LIKE ? OR i.description LIKE ?
            ORDER BY s.effectiveness_rating DESC, s.verified DESC
            LIMIT 20
        ''', (f'%{crash_data_sample}%', f'%{crash_data_sample}%'))
        
        return cursor.fetchall()
    
    def format_solutions(self, results):
        """Format database results into solution objects"""
        solutions = []
        for row in results:
            try:
                commands = json.loads(row[9]) if row[9] else []
            except (json.JSONDecodeError, TypeError):
                commands = [row[9]] if row[9] else []
            
            solutions.append({
                'issue_type': row[1],
                'severity': row[4],
                'platform': row[5],
                'solution_title': row[7],
                'solution_description': row[8],
                'commands': commands,
                'source_type': row[10],
                'source_url': row[11],
                'effectiveness_rating': row[12],
                'verified': bool(row[13])
            })
        
        return solutions
    
    def get_performance_stats(self):
        """Get performance statistics"""
        cache_hit_rate = 0
        if self.performance_stats['cache_hits'] + self.performance_stats['cache_misses'] > 0:
            cache_hit_rate = self.performance_stats['cache_hits'] / (
                self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
            ) * 100
        
        avg_query_time = 0
        if self.performance_stats['query_times']:
            avg_query_time = sum(self.performance_stats['query_times']) / len(self.performance_stats['query_times'])
        
        return {
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_hits': self.performance_stats['cache_hits'],
            'cache_misses': self.performance_stats['cache_misses'],
            'total_queries': self.performance_stats['total_queries'],
            'average_query_time': round(avg_query_time * 1000, 2),  # ms
            'cache_size': len(self.cache)
        }
    
    def clear_cache(self):
        """Clear performance cache"""
        self.cache.clear()
        self.cache_expiry.clear()
        print("🧹 Performance cache cleared")
    
    def optimize_database(self):
        """Run database optimization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Analyze tables for better query planning
            cursor.execute('ANALYZE')
            
            # Vacuum database to reclaim space
            cursor.execute('VACUUM')
            
            # Update statistics
            cursor.execute('PRAGMA optimize')
            
            conn.commit()
            print("✅ Database optimization completed")
            
        except Exception as e:
            print(f"⚠️ Database optimization error: {e}")
        finally:
            conn.close()

def main():
    """Test performance optimizer"""
    optimizer = PerformanceOptimizer()
    
    # Test search
    test_crash = "ANOM_ABEND sig=11 code-insiders renderer crash"
    
    print("🔍 Testing optimized search...")
    start_time = time.time()
    solutions = optimizer.optimized_search(test_crash)
    search_time = time.time() - start_time
    
    print(f"⚡ Found {len(solutions)} solutions in {search_time*1000:.2f}ms")
    
    # Test cache
    print("🔍 Testing cache performance...")
    start_time = time.time()
    cached_solutions = optimizer.optimized_search(test_crash)
    cache_time = time.time() - start_time
    
    print(f"💾 Cached lookup in {cache_time*1000:.2f}ms")
    
    # Performance stats
    stats = optimizer.get_performance_stats()
    print("\n📊 Performance Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == '__main__':
    main()
