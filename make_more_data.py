import csv, random

seed_benign = [
  "hello world",
  "select * from employees where id = 5",
  "product search: laptop bag",
  "INSERT INTO logs(message) VALUES('user signed in')",
  "email=jane.doe@example.com&reset=true",
  "order by date desc",
  "price between 100 and 200",
  "normal text without sql",
  "department='economy' and region='apac'",
  "update profile set city='Hyderabad' where user_id=10",
]

seed_attacks = [
  "' OR 1=1 --",
  "admin' --",
  "1; WAITFOR DELAY '0:0:5' --",
  "UNION SELECT username, password FROM users --",
  "' UNION SELECT null,null --",
  "' OR '1'='1",
  "\" OR \"\" = \"",
  "') OR ('1'='1",
  "' ; DROP TABLE users; --",
  "1 AND SLEEP(5)--",
  "'/**/OR/**/1=1--",
  "-1' UNION ALL SELECT 1,2--",
]

def perturb(s):
    # random spacing, case changes, insert comments/extra quotes
    s2 = s
    if random.random() < 0.5:
        s2 = s2.replace(" ", random.choice([" ", "  ", " /**/ "]))
    if random.random() < 0.5:
        s2 = "".join(c.upper() if random.random()<0.3 else c for c in s2)
    if random.random() < 0.3:
        s2 = s2.replace("--", random.choice(["--", "#", ";--"]))
    return s2

rows = []
for _ in range(400):
    rows.append([random.choice(seed_benign), 0])
for _ in range(400):
    rows.append([perturb(random.choice(seed_attacks)), 1])

random.shuffle(rows)

with open("data/sql_payloads.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text","label"])
    w.writerows(rows)

print("Wrote ~800 rows to data/sql_payloads.csv")