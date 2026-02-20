import asyncio
from pathlib import Path
from typing import List, Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


async def run_concurrent_tasks(
    tasks: List[Callable],
    max_workers: int = 4,
    show_progress: bool = True
) -> List[Any]:
    """
    Run multiple tasks concurrently.
    
    Args:
        tasks: List of callable functions to execute
        max_workers: Maximum number of concurrent workers
        show_progress: Whether to show progress messages
    
    Returns:
        List of results in the same order as tasks
    """
    from ..utils.logging import get_logger
    logger = get_logger("concurrent")
    
    results = [None] * len(tasks)
    
    if show_progress:
        logger.info(f"Running {len(tasks)} tasks concurrently with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(task): idx
            for idx, task in enumerate(tasks)
        }
        
        completed = 0
        for future in as_completed(futures.keys()):
            idx = futures[future]
            try:
                results[idx] = future.result()
                completed += 1
                
                if show_progress and completed % 10 == 0:
                    logger.info(f"Completed {completed}/{len(tasks)} tasks")
            except Exception as e:
                logger.error(f"Task {idx} failed: {str(e)}")
                results[idx] = None
    
    if show_progress:
        logger.info(f"Completed all {len(tasks)} tasks")
    
    return results


async def read_multiple_files_async(file_paths: List[str]) -> List[Optional[str]]:
    """
    Read multiple files concurrently.
    
    Args:
        file_paths: List of file paths to read
    
    Returns:
        List of file contents (None if file doesn't exist)
    """
    from ..tools.file_tools import read_file
    
    tasks = [lambda fp=file_path: read_file(fp) for file_path in file_paths]
    
    return await run_concurrent_tasks(tasks)


async def write_multiple_files_async(file_content_pairs: List[tuple[str, str]]) -> List[bool]:
    """
    Write multiple files concurrently.
    
    Args:
        file_content_pairs: List of (file_path, content) tuples
    
    Returns:
        List of success flags for each file write
    """
    from ..tools.file_tools import write_file
    
    async def write_file_safe(file_path: str, content: str) -> bool:
        try:
            write_file(file_path, content)
            return True
        except Exception:
            return False
    
    tasks = [
        lambda pair=pair: write_file_safe(pair[0], pair[1])
        for pair in file_content_pairs
    ]
    
    return await run_concurrent_tasks(tasks)


async def process_files_concurrently(
    file_paths: List[str],
    process_func: Callable[[str, str], Any],
    max_workers: int = 4
) -> List[Any]:
    """
    Process multiple files concurrently with a custom function.
    
    Args:
        file_paths: List of file paths to process
        process_func: Function that takes (file_path, file_content) and returns result
        max_workers: Maximum number of concurrent workers
    
    Returns:
        List of results from processing each file
    """
    from ..tools.file_tools import read_file
    from ..utils.logging import get_logger
    
    logger = get_logger("concurrent")
    
    async def process_single_file(file_path: str) -> Any:
        try:
            content = read_file(file_path)
            if content.startswith("Error"):
                logger.warning(f"Could not read {file_path}")
                return None
            return process_func(file_path, content)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None
    
    tasks = [process_single_file for file_path in file_paths]
    
    return await run_concurrent_tasks(tasks, max_workers)


class RateLimiter:
    """
    Rate limiter to control concurrent operations.
    """
    
    def __init__(self, max_concurrent: int = 10):
        self._max_concurrent = max_concurrent
        self._current = 0
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def acquire(self):
        """Acquire permission to proceed."""
        await self._semaphore.acquire()
        self._current += 1
    
    async def release(self):
        """Release permission after completing."""
        self._semaphore.release()
        self._current -= 1
    
    @property
    def current(self) -> int:
        """Current number of active operations."""
        return self._current
    
    @property
    def available(self) -> int:
        """Available slots for operations."""
        return self._max_concurrent - self._current


async def with_rate_limiter(
    limiter: RateLimiter,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with rate limiting.
    
    Args:
        limiter: RateLimiter instance
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Result of function execution
    """
    await limiter.acquire()
    try:
        return await func(*args, **kwargs)
    finally:
        limiter.release()
