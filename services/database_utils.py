"""
Database utilities for performance optimization and monitoring
"""
import logging
from django.db import connection
from django.core.cache import cache
from functools import wraps
import time

logger = logging.getLogger(__name__)


def monitor_queries(func):
    """Decorator to monitor database queries for a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            duration = end_time - start_time
            
            if query_count > 10 or duration > 0.5:  # Log slow or query-heavy operations
                logger.warning(
                    f"Function {func.__name__} executed in {duration:.3f}s with {query_count} queries"
                )
    
    return wrapper


def cache_result(timeout=300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # If not in cache, execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def bulk_create_with_chunks(model, objects, chunk_size=1000):
    """
    Bulk create objects in chunks to avoid memory issues with large datasets
    """
    total_created = 0
    for i in range(0, len(objects), chunk_size):
        chunk = objects[i:i + chunk_size]
        created = model.objects.bulk_create(chunk, ignore_conflicts=True)
        total_created += len(created)
        logger.info(f"Created {len(created)} {model.__name__} objects (chunk {i//chunk_size + 1})")
    
    return total_created


def optimize_queryset(queryset, select_related_fields=None, prefetch_related_fields=None):
    """
    Apply select_related and prefetch_related optimizations to a queryset
    """
    if select_related_fields:
        queryset = queryset.select_related(*select_related_fields)
    
    if prefetch_related_fields:
        queryset = queryset.prefetch_related(*prefetch_related_fields)
    
    return queryset


def get_slow_queries(threshold=1.0):
    """
    Get queries that took longer than the threshold
    """
    slow_queries = []
    for query in connection.queries:
        if float(query.get('time', 0)) > threshold:
            slow_queries.append({
                'sql': query.get('sql', ''),
                'time': query.get('time', 0),
                'raw_sql': query.get('raw_sql', '')
            })
    return slow_queries


def log_query_performance():
    """
    Log current query performance statistics
    """
    queries = connection.queries
    if queries:
        total_time = sum(float(q.get('time', 0)) for q in queries)
        avg_time = total_time / len(queries)
        logger.info(f"Query performance: {len(queries)} queries, "
                   f"total time: {total_time:.3f}s, avg time: {avg_time:.3f}s")
        
        # Log slow queries
        slow_queries = get_slow_queries(0.1)  # Queries taking more than 100ms
        if slow_queries:
            logger.warning(f"Found {len(slow_queries)} slow queries (>100ms)")
            for query in slow_queries[:5]:  # Log first 5 slow queries
                logger.warning(f"Slow query ({query['time']}s): {query['sql'][:200]}...")


class QueryOptimizer:
    """Class for optimizing common query patterns"""
    
    @staticmethod
    def optimize_student_queryset(queryset):
        """Optimize student-related queries"""
        return queryset.select_related(
            'user', 'programme', 'cohort', 'campus'
        ).prefetch_related(
            'studentdocument_set', 'studenteducationhistory_set'
        )
    
    @staticmethod
    def optimize_staff_queryset(queryset):
        """Optimize staff-related queries"""
        return queryset.select_related(
            'user', 'department', 'position', 'campus'
        ).prefetch_related(
            'staffpayroll', 'staffdocuments', 'staffleaveentitlement_set'
        )
    
    @staticmethod
    def optimize_library_queryset(queryset):
        """Optimize library-related queries"""
        return queryset.select_related(
            'book', 'member', 'issued_by'
        ).prefetch_related(
            'fine_set'
        )
