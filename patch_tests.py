import os
import re

for filename in ["tests/test_results_and_analytics.py", "tests/test_reviewer_assignment.py", "tests/test_evaluations.py"]:
    with open(filename, "r") as f:
        content = f.read()
    
    # We want to find: var = client.post("/api/reviewers/"...
    # and add: client.patch(f"/api/reviewers/{var['id']}/status", json={"status": "approved"}, headers=organizer_headers)
    
    # first, revert the bad sed
    content = re.sub(r' +client\.patch.*rev1.*?\n', '', content)
    
    # now apply correctly
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        m = re.match(r'^(\s+)([a-zA-Z0-9_]+)\s*=\s*client\.post\(\s*"/api/reviewers/"', line)
        if m:
            indent = m.group(1)
            var_name = m.group(2)
            # Find if headers=organizer_headers is used in the file
            new_lines.append(f'{indent}client.patch(f"/api/reviewers/{{{var_name}[\'id\']}}/status", json={{"status": "approved"}}, headers=organizer_headers)')
            
    with open(filename, "w") as f:
        f.write('\n'.join(new_lines))

