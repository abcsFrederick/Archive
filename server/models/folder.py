import os
from girder.models.setting import Setting
from girder.api.rest import Resource
from girder.exceptions import GirderException

from ..external.mariadb_proxy import MariadbProxy
from ..external.postgre_proxy import PostgredbProxy
import psycopg2.extras


class Folder(Resource):
    def __init__(self):
        self.name = 'SAIPArchiveFolderModel'
        super(Folder, self).__init__()
        self.user = self.getCurrentUser()
        self.MariaDB = MariadbProxy().conn
        self.PostgreDB = PostgredbProxy().conn
        self.MariaCursor = self.MariaDB.cursor(buffered=True, dictionary=True)
        self.PostgreCursor = self.PostgreDB.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.root = Setting().get('Archive.SCIPPYMOUNT')

    def find(self, parentId, parentType, text=None):
        if parentType == 'user':
            result = self.getProjects(text, self.user)
        elif parentType == 'project':
            result = self.getExperiments(parentId)
        elif parentType == 'experiment':
            result = self.getPatients(parentId)
        elif parentType == 'patient':
            result = self.getStudies(parentId)

        return result

    def getProjects(self, text, user=None):
        self.MariaCursor.execute("SELECT * FROM site_users WHERE userId=%s", (user['login'],))

        rows = [row for row in self.MariaCursor]
        if len(rows):
            for row in rows:
                userid = row['id']
        else:
            self.MariaCursor.close()
            raise GirderException('Not a registored user of SAIP')

        self.MariaCursor.execute("SELECT group_id FROM site_group_memberships WHERE person_id=%s",
                                 (str(userid),))

        admin = False
        for row in self.MariaCursor:
            if row['group_id'] == 7:
                admin = True
                break

        projects = []
        if admin:
            self.MariaCursor.execute("SELECT nci_projects_created_at,nci_projects_id, "
                                     "nci_projects_name, nci_projects_pi_id,"
                                     "Pi_First_name, Pi_Last_name, number_of_experiments, "
                                     "number_of_studies, projects_status, number_of_images,"
                                     "GROUP_CONCAT(short_name) AS short_name FROM "
                                     "(SELECT t5.*, nci_protocol_categories.short_name FROM "
                                     "(SELECT t4.*, nci_protocols.protocol_category_id FROM "
                                     "(SELECT t3.*,COUNT(imaging_experiments.title) AS "
                                     "number_of_experiments, "
                                     "SUM(IFNULL(imaging_experiments.number_of_studies,0)) "
                                     "AS number_of_studies,  "
                                     "SUM(IFNULL(imaging_experiments.number_of_images,0)) "
                                     "AS number_of_images FROM "
                                     "(SELECT t2.*, site_users.last_name AS Pi_Last_name, "
                                     "site_users.first_name "
                                     "AS Pi_First_name FROM"
                                     "(SELECT nci_projects.id AS nci_projects_id,nci_projects.name "
                                     "AS nci_projects_name,"
                                     "nci_projects.pi_id AS nci_projects_pi_id,status "
                                     "AS projects_status, created_at "
                                     "AS nci_projects_created_at FROM "
                                     "nci_projects) as t2 LEFT JOIN "
                                     "site_users ON t2.nci_projects_pi_id=site_users.id) "
                                     "as t3 LEFT JOIN imaging_experiments ON "
                                     "t3.nci_projects_id=imaging_experiments.project_id GROUP BY "
                                     "t3.nci_projects_id) as t4 LEFT JOIN nci_protocols "
                                     "ON t4.nci_projects_id=nci_protocols.project_id) "
                                     "as t5 LEFT JOIN "
                                     "nci_protocol_categories ON "
                                     "t5.protocol_category_id=nci_protocol_categories.id) "
                                     "AS t6 GROUP BY nci_projects_id;")
            for row in self.MariaCursor:
                projects.append(row)
        else:
            self.MariaCursor.execute(
                "SELECT * FROM "
                "(SELECT project_id FROM nci_project_users WHERE user_id=%s)"
                " as t1 LEFT JOIN nci_projects ON project_id=nci_projects.id",
                (str(userid),))
            for row in self.MariaCursor:
                projects.append(row)
        self.MariaCursor.close()
        self.MariaDB.close()
        return projects

    def getExperiments(self, projectId):
        self.MariaCursor.execute("SELECT * FROM imaging_experiments WHERE project_id=%s",
                                 (projectId,))
        experiments = self.MariaCursor.fetchall()
        self.MariaCursor.close()
        self.MariaDB.close()
        return experiments

    def getPatients(self, experimentId):
        self.MariaCursor.execute("SELECT * FROM imaging_participants WHERE experiment_id=%s",
                                 (experimentId,))

        patients = []

        for row in self.MariaCursor:
            patients.append(row['patient_id'])
        self.MariaCursor.close()
        self.MariaDB.close()

        try:
            self.PostgreCursor.execute("""SELECT id, pat_name,
                                       pat_mrn, pat_path FROM patients WHERE id IN %s""",
                                       (tuple(patients),))
        except Exception as e:
            print e
            raise GirderException('Query failed when SELECT from studies')

        rows = self.PostgreCursor.fetchall()
        self.PostgreCursor.close()
        self.PostgreDB.close()
        return rows

    def getStudies(self, patientId):
        try:
            self.PostgreCursor.execute("""SELECT id,studyid,study_path,
            study_description FROM studies WHERE pat_id=%s""" % patientId)
        except Exception:
            raise GirderException('Query failed when SELECT from studies')

        rows = self.PostgreCursor.fetchall()

        self.PostgreCursor.close()
        self.PostgreDB.close()
        return rows

    def fullPath(self, id, type):
        if type == 'project':
            # result = self.getExperiments(id)
            pass
        elif type == 'experiment':
            # result = self.getPatients(id)
            pass
        elif type == 'patient':
            try:
                self.PostgreCursor.execute(
                    """SELECT id,pat_path,pat_name FROM
                    patients WHERE id = %s""",
                    (id,))
            except Exception:
                raise GirderException('Query failed when SELECT from patients')

            rows = self.PostgreCursor.fetchall()
            if len(rows):
                row = rows[0]
                self.PostgreCursor.close()
                self.PostgreDB.close()
                if row['pat_path'] is not None:
                    path = os.path.join(self.root,
                                        row['pat_path'])
                    return row['pat_name'], path
                else:
                    raise GirderException('Rows with id:%s does not have [ pat_path ]' % row['id'])
            else:
                raise GirderException('No patient: %s ' % id)
        elif type == 'study':
            try:
                self.PostgreCursor.execute(
                    """SELECT t1.*,pat_path,pat_name FROM
                    (SELECT id,study_path,pat_id,study_description FROM
                    studies WHERE id = %s) AS t1 LEFT JOIN patients ON patients.id=t1.pat_id;""",
                    (id,))
            except Exception:
                raise GirderException('Query failed when SELECT from studies')

            rows = self.PostgreCursor.fetchall()
            if len(rows):
                row = rows[0]
                self.PostgreCursor.close()
                self.PostgreDB.close()
                if row['pat_path'] is not None\
                        and row['study_path'] is not None:
                    path = os.path.join(self.root,
                                        row['pat_path'],
                                        row['study_path'])
                    return row['study_description'], path
                else:
                    raise GirderException('Rows with id:%s does not have'
                                          ' [ pat_path, study_path]' % row['id'])
            else:
                raise GirderException('No study: %s' % id)
