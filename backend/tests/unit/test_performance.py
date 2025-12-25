"""
Performance tests for KrediPlus API
"""
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from src.main import app


class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    def test_health_endpoint_response_time(self):
        """Health endpoint should respond under 100ms"""
        client = TestClient(app)
        
        start_time = time.perf_counter()
        response = client.get("/health")
        duration = time.perf_counter() - start_time
        
        assert response.status_code == 200
        assert duration < 0.1  # 100ms
        assert response.json() == {"status": "healthy"}
    
    def test_concurrent_requests_simulation(self):
        """Simulate concurrent requests by making multiple sequential calls"""
        client = TestClient(app)
        times = []
        
        # Make 10 sequential requests to simulate load
        for _ in range(10):
            start_time = time.perf_counter()
            response = client.get("/health")
            duration = time.perf_counter() - start_time
            times.append(duration)
            
            assert response.status_code == 200
        
        # Calculate statistics
        avg_duration = sum(times) / len(times)
        max_duration = max(times)
        
        # Performance assertions
        assert avg_duration < 0.1  # 100ms average
        assert max_duration < 0.2  # 200ms maximum
    
    def test_memory_usage_stability(self):
        """Memory usage should remain stable across multiple requests"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        client = TestClient(app)
        
        # Make 50 requests
        for _ in range(50):
            response = client.get("/health")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024  # 50MB


@pytest.mark.slow
class TestEndpointPerformanceBenchmarks:
    """Detailed performance benchmarks for each endpoint"""
    
    def test_health_endpoint_benchmark(self):
        """Benchmark health endpoint performance"""
        client = TestClient(app)
        times = []
        
        # Run 20 times for better statistics
        for _ in range(20):
            start_time = time.perf_counter()
            response = client.get("/health")
            duration = time.perf_counter() - start_time
            times.append(duration)
            
            assert response.status_code == 200
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        # Performance assertions
        assert avg_time < 0.05  # 50ms average
        assert max_time < 0.1   # 100ms maximum
        
        # Print results for analysis
        print(f"\n=== Health Endpoint Performance ===")
        print(f"Average: {avg_time:.4f}s ({avg_time*1000:.1f}ms)")
        print(f"Maximum: {max_time:.4f}s ({max_time*1000:.1f}ms)")
        print(f"Minimum: {min_time:.4f}s ({min_time*1000:.1f}ms)")
    
    def test_multiple_endpoints_benchmark(self):
        """Benchmark multiple endpoints"""
        client = TestClient(app)
        
        endpoints = ["/health"]  # Solo health por ahora (otros requieren auth)
        
        results = {}
        
        for endpoint in endpoints:
            times = []
            
            # Run each endpoint 10 times
            for _ in range(10):
                start_time = time.perf_counter()
                response = client.get(endpoint)
                duration = time.perf_counter() - start_time
                times.append(duration)
                
                assert response.status_code == 200
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            results[endpoint] = {
                "avg": avg_time,
                "max": max_time,
                "min": min_time
            }
            
            # Performance assertions
            assert avg_time < 0.1  # 100ms average
            assert max_time < 0.2  # 200ms maximum
        
        # Print benchmark results
        print(f"\n=== Multi-Endpoint Performance Benchmark ===")
        for endpoint, stats in results.items():
            print(f"{endpoint}:")
            print(f"  Avg: {stats['avg']:.4f}s ({stats['avg']*1000:.1f}ms)")
            print(f"  Max: {stats['max']:.4f}s ({stats['max']*1000:.1f}ms)")
            print(f"  Min: {stats['min']:.4f}s ({stats['min']*1000:.1f}ms)")
