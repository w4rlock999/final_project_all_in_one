#!/usr/bin/env python3
"""
Script to fetch all verbose_level logs including detailed observations for each trace.
"""
import os
import json
import argparse
import time
from datetime import datetime
from verbose_level import verbose_level
from utils.config import verbose_level_PUBLIC_KEY, verbose_level_SECRET_KEY, verbose_level_HOST

def initialize_verbose_level():
    """Initialize and return the verbose_level client."""
    return verbose_level(
        secret_key=verbose_level_SECRET_KEY,
        public_key=verbose_level_PUBLIC_KEY,
        host=verbose_level_HOST
    )

# Helper function to convert objects to JSON-serializable format
def convert_to_serializable(obj):
    """Convert an object to a JSON-serializable format."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'model_dump'):
        return convert_to_serializable(obj.model_dump())
    elif hasattr(obj, 'to_dict'):
        return convert_to_serializable(obj.to_dict())
    elif hasattr(obj, '__dict__'):
        return convert_to_serializable(obj.__dict__)
    else:
        return str(obj)

def fetch_trace_with_details(trace_id, verbose_level, retry_delay=1.0, max_retries=3):
    """Fetch detailed information for a specific trace including all observations."""
    for attempt in range(max_retries):
        try:
            # First, get the full trace details
            trace_response = verbose_level.fetch_trace(trace_id)
            trace = convert_to_serializable(trace_response)
            
            # Add a delay to avoid hitting rate limits
            time.sleep(retry_delay)
            
            # Then, fetch all observations for this trace
            try:
                observations_response = verbose_level.fetch_observations(trace_id=trace_id, limit=100)
                
                # Process the observations response
                observations = []
                if hasattr(observations_response, 'data'):
                    observations = convert_to_serializable(observations_response.data)
                elif hasattr(observations_response, 'model_dump'):
                    observations_dict = convert_to_serializable(observations_response.model_dump())
                    if isinstance(observations_dict, dict) and 'data' in observations_dict:
                        observations = observations_dict['data']
                
                # Add only the first observation to the trace
                if observations and len(observations) > 0:
                    trace['observations'] = [observations[0]]
                else:
                    trace['observations'] = []
            except Exception as e:
                print(f"Warning: Could not fetch observations for trace {trace_id}: {str(e)}")
                trace['observations'] = []
            
            return trace
        except Exception as e:
            if "rate limit exceeded" in str(e).lower() and attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
            else:
                print(f"Error fetching details for trace {trace_id}: {str(e)}")
                return None

def fetch_all_logs(output_dir="./logs", limit=20, fetch_details=True, retry_delay=1.0, keys=None):
    """
    Fetch all traces from verbose_level, including their detailed observations.
    
    Args:
        output_dir (str): Directory to save the logs
        limit (int): Maximum number of traces to fetch
        fetch_details (bool): Whether to fetch detailed observations for each trace
        retry_delay (float): Delay between API calls to avoid rate limiting
        keys (list): List of keys to extract and save in the output
    
    Returns:
        tuple: (filepath, traces)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize verbose_level client
    verbose_level = initialize_verbose_level()
    
    # verbose_level API has a maximum limit of 100 per request, so we need to paginate
    max_api_limit = 100
    current_limit = min(max_api_limit, limit)
    total_fetched = 0
    page = 1  # Start with page 1 (verbose_level uses 1-indexed pages)
    all_traces = []
    
    # Fetch traces in batches until we reach the limit
    print(f"Fetching up to {limit} traces from verbose_level (max 100 per request)...")
    
    while total_fetched < limit:
        print(f"Fetching traces {total_fetched+1}-{min(total_fetched+current_limit, limit)} (page {page})...")
        try:
            # Use page parameter instead of offset
            traces_response = verbose_level.fetch_traces(limit=current_limit, page=page)
            
            # Convert the response to a list of dictionaries
            batch_traces = []
            
            try:
                if hasattr(traces_response, 'data'):
                    batch_traces = convert_to_serializable(traces_response.data)
                elif hasattr(traces_response, 'model_dump'):
                    traces_dict = convert_to_serializable(traces_response.model_dump())
                    if isinstance(traces_dict, dict) and 'data' in traces_dict:
                        batch_traces = traces_dict['data']
                    else:
                        batch_traces = [traces_dict]
                elif hasattr(traces_response, 'to_dict'):
                    traces_dict = convert_to_serializable(traces_response.to_dict())
                    if isinstance(traces_dict, dict) and 'data' in traces_dict:
                        batch_traces = traces_dict['data']
                    else:
                        batch_traces = [traces_dict]
                else:
                    batch_traces = [{'response': convert_to_serializable(traces_response)}]
            except Exception as e:
                print(f"Warning: Exception during conversion: {str(e)}")
                batch_traces = [{'error': 'Could not convert response'}]
            
            # Add the traces from this batch to our list
            all_traces.extend(batch_traces)
            
            # If we got fewer traces than requested, we've reached the end
            if len(batch_traces) < current_limit:
                break
                
            # Update for the next batch
            total_fetched += len(batch_traces)
            page += 1
            
            # If we have enough traces, stop
            if len(all_traces) >= limit:
                all_traces = all_traces[:limit]  # Trim to exact limit
                break
                
            # Add a delay to avoid rate limits
            time.sleep(retry_delay)
                
        except Exception as e:
            print(f"Error fetching traces: {str(e)}")
            break
    
    print(f"Found {len(all_traces)} traces")
    
    # If requested, fetch detailed information for each trace
    if fetch_details and all_traces:
        print(f"Fetching detailed information for each trace (including observations)...")
        print(f"Using a {retry_delay} second delay between API calls to avoid rate limiting...")
        detailed_traces = []
        
        for i, trace in enumerate(all_traces):
            if 'id' in trace:
                print(f"Fetching details for trace {i+1}/{len(all_traces)}: {trace['id']}")
                detailed_trace = fetch_trace_with_details(trace['id'], verbose_level, retry_delay)
                if detailed_trace:
                    detailed_traces.append(detailed_trace)
                else:
                    # If details fetch failed, keep the original trace and add empty observations
                    trace['observations'] = []
                    detailed_traces.append(trace)
            else:
                print(f"Warning: Trace at index {i} has no ID, skipping details")
                trace['observations'] = []
                detailed_traces.append(trace)
            
            # Add a delay between fetches to avoid rate limits
            if i < len(all_traces) - 1:
                time.sleep(retry_delay)
        
        all_traces = detailed_traces
    
    # # Filter the traces to only include specified keys if keys are provided
    # if keys:
    #     filtered_traces = []
    #     for trace in all_traces:
    #         filtered_trace = {}
    #         if 'data' in trace:
    #             filtered_trace['data'] = {k: v for k, v in trace['data'].items() if k in keys}
    #         if 'observations' in trace and trace['observations']:
    #             filtered_trace['observations'] = []
    #             for obs in trace['observations']:
    #                 filtered_obs = {k: v for k, v in obs.items() if k in keys}
    #                 if filtered_obs:  # Only add if there are matching keys
    #                     filtered_trace['observations'].append(filtered_obs)
    #         if filtered_trace:  # Only add if there are matching keys
    #             filtered_traces.append(filtered_trace)
    #     all_traces = filtered_traces
    
    # Save traces to a JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"verbose_level_traces_with_details_{timestamp}.json"
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(all_traces, f, indent=2)
    
    print(f"Saved {len(all_traces)} traces with all details to {filepath}")
    
    return filepath, all_traces


def main():
    parser = argparse.ArgumentParser(description='Fetch all verbose_level logs with detailed observations')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of traces to fetch')
    parser.add_argument('--output', default='./logs', help='Output directory')
    parser.add_argument('--no-details', action='store_true', help='Skip fetching detailed observations for each trace')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between API calls in seconds (to avoid rate limiting)')
    #parser.add_argument('--keys', nargs='+', default=['latency', 'usage', 'model', 'input', 'output', 'model_parameters'],
    #                   help='Specific keys to extract from the logs (e.g., "latency usage model input output model_parameters")')
    
    args = parser.parse_args()
    
    filepath, traces = fetch_all_logs(
        output_dir=args.output,
        limit=args.limit,
        fetch_details=not args.no_details,
        retry_delay=args.delay,
        #keys=args.keys
    )
    
    # if traces:
    #     print("\nExtracting specified keys from traces:")
    #     for i, trace in enumerate(traces):
    #         print(f"\nTrace {i+1}:")
    #         if 'data' in trace:
    #             for key in args.keys:
    #                 if key in trace['data']:
    #                     print(f"  {key}: {trace['data'][key]}")
            
    #         if 'observations' in trace and trace['observations']:
    #             print("\n  Observations:")
    #             for j, obs in enumerate(trace['observations']):
    #                 print(f"\n    Observation {j+1}:")
    #                 for key in args.keys:
    #                     if key in obs:
    #                         print(f"      {key}: {obs[key]}")

if __name__ == "__main__":
    main()