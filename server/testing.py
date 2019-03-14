import mysql.connector as mariadb
import psycopg2
import psycopg2.extras

try:
    mariadb_connection = mariadb.connect(host='fr-s-mysql-4.ncifcrf.gov',
                                         port='3306', user='miaot2',
                                         password='Luying_0325', database='IVG')
    print "I am able to connect to fr-s-mysql-4 database"
except mariadb.Error as error:
    print("Error: {}".format(error))

cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
cursor.execute("SELECT * FROM imaging_experiments WHERE project_id=%s", (id,))

experiments = []
for row in cursor:
    experiments.append(row['id'])

cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
if len(experiments) == 1:
    experiments = experiments
    cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id = %s" % experiments[0])

else:
    experiments = tuple(experiments)
    cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id in %s" % (experiments,))

patients = []

for row in cursor:
    patients.append(row['patient_id'])
cursor.close()
mariadb_connection.close()

try:
    conn = psycopg2.connect("dbname='miaot2' user='miaot2' host='ivg-boxx' password='luying0325'")
    print "I am able to connect to the database"
except Exception:
    print "I am unable to connect to the database"
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

try:
    cur.execute(
        """SELECT t2.*,series_path FROM
         (SELECT t1.*,id AS study_id,study_path FROM
         (SELECT id AS pat_id, pat_path FROM patients WHERE id in %s)
         AS t1 LEFT JOIN studies ON t1.pat_id =studies.pat_id)
         AS t2 LEFT JOIN series ON t2.study_id = series.study_id""",
        (tuple(patients),))
except Exception:
    print "I can't SELECT from studies"

series_roots_obj = {'series_roots': []}

for row in cur:
    if row['pat_path'] is not None\
            and row['study_path'] is not None\
            and row['series_path'] is not None:
        series_roots_obj['series_roots'].append(row['pat_path']
                                                + '/' + row['study_path']
                                                + '/' + row['series_path'])

print series_roots_obj
# return projects
