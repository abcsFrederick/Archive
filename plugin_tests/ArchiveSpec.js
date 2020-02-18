girderTest.importPlugin('Archive');
girderTest.startApp();

function _createFolder(id, name, type) {
    var Model;
    Model = new girder.plugins.Archive.models.FolderModel();
    if (type === 'projects') {
        Model.set({
            Pi_First_name: type + '_TEST_' + id,
            Pi_Last_name: type + '_TEST_' + id,
            nci_projects_created_at: '2010-09-14T22:17:09+00:00',
            nci_projects_id: id,
            nci_projects_name: name,
            nci_projects_pi_id: 999,
            number_of_experiments: 999,
            number_of_images: '999',
            number_of_studies: '999',
            projects_status: 'I',
            short_name: 'BLIAN'
        });
    } else if (type === 'experiments') {
        Model.set({
            created_at: '2006-03-31T00:00:00+00:00',
            description: name,
            id: id,
            miportal_id: 11,
            mouse_id: null,
            number_of_images: 1679,
            number_of_series: 53,
            number_of_studies: 37,
            pi_id: 6,
            probe_id: null,
            project_id: 1,
            start_date: '2006-03-31',
            title: name,
            type: 'Nci::Experiment',
            updated_at: '2010-09-29T16:49:00+00:00'
        });
    }
    return Model;
}

// function _createItem(id, name, type) {
//     var Model;
//     Model = new girder.plugins.Archive.models.FolderModel();
//     if (type === 'series') {
//         Model.set({
//             id: id,
//             modality: name,
//             series_description: name,
//             series_path: '00007082',
//             series_uid: '1.3.12.2.1107.5.8.2.12345.2004113121559250.18380'
//         });
//     }
//     return Model;
// }
$(function () {
    describe('Archive project, experiment, patient, study, series list view', function () {
        var testEl, archiveView, projectModel1, projectModel2, experimentModel1,
            experimentModel2; // seriesModel1, seriesModel2;
        it('create the admin user', function () {
            girderTest.createUser(
                'test', 'test@nih.gov', 'Admin', 'Admin', 'testpassword')();
        });
        it('Projects fetch under current nih user', function () {
            runs(function () {
                testEl = $('<div/>').appendTo('body');
                archiveView = new girder.plugins.Archive.views.body.ArchiveView({
                    el: testEl,
                    parentView: null
                });
            });
            waitsFor(function () {
                return archiveView.$('.g-archive-hierarchy-container').length === 1 &&
                       archiveView.$('.g-hierarchy-breadcrumb-bar').length === 1 &&
                       archiveView.$('.g-folder-list-container').length === 1 &&
                       archiveView.$('.g-item-list-container').length === 1;
            }, 'SAIP archive container created');
            runs(function () {
                expect(archiveView.hierarchyWidget.folderListView.collection.length).toBe(0);
                expect(archiveView.$('.breadcrumb .active').text()).toBe('Projects');
                projectModel1 = _createFolder(99998, 'project_1', 'projects');
                projectModel2 = _createFolder(99999, 'project_2', 'projects');
                archiveView.hierarchyWidget.folderListView.collection.add([projectModel1, projectModel2]);
                archiveView.hierarchyWidget.folderListView.render();
            });
            waitsFor(function () {
                return archiveView.$('.archive-folder-list-link').length === 2;
            }, 'SAIP archive projects list rendered as folder');
            runs(function () {
                expect($(archiveView.$('.archive-folder-list-link')[0]).text()).toBe('project_1');
                expect($(archiveView.$('.archive-folder-list-link')[1]).text()).toBe('project_2');
            });
        });
        it('Experients fetch under current project', function () {
            runs(function () {
                $(archiveView.$('.archive-folder-list-link'))[0].click();
            });
            waitsFor(function () {
                return archiveView.$('.breadcrumb .active').text() === 'project_1';
            }, 'project_1 is click and render experiments underneath');
            runs(function () {
                expect(archiveView.hierarchyWidget.folderListView.collection.length).toBe(0);
                experimentModel1 = _createFolder(99998, 'experiment_1', 'experiments');
                experimentModel2 = _createFolder(99999, 'experiment_2', 'experiments');
                archiveView.hierarchyWidget.folderListView.collection.add([experimentModel1, experimentModel2]);
                archiveView.hierarchyWidget.folderListView.render();
            });
            waitsFor(function () {
                return archiveView.$('.archive-folder-list-link').length === 2;
            }, 'SAIP archive experiments list rendered as folder');
            runs(function () {
                expect($(archiveView.$('.archive-folder-list-link')[0]).text()).toBe('experiment_1');
                expect($(archiveView.$('.archive-folder-list-link')[1]).text()).toBe('experiment_2');
            });
        });
        // it('Series fetch under current study', function () {
        //     runs(function () {
        //         $(archiveView.$('.archive-folder-list-link'))[0].click();
        //     });
        //     waitsFor(function () {
        //         return archiveView.$('.breadcrumb .active').text() === 'experiment_1';
        //     }, 'study_1 is click and render series underneath');
        //     runs(function () {
        //         expect(archiveView.hierarchyWidget.itemListView.collection.length).toBe(0);
        //         seriesModel1 = _createItem(99998, 'series_1', 'series');
        //         seriesModel2 = _createItem(99999, 'series_2', 'series');
        //         archiveView.hierarchyWidget.itemListView.collection.add([seriesModel1, seriesModel2]);
        //         archiveView.hierarchyWidget.itemListView.render();
        //     });
        //     waitsFor(function () {
        //         return archiveView.$('.archive-item-list-link').length === 2;
        //     }, 'SAIP archive series list rendered as item');
        //     runs(function () {
        //         expect($(archiveView.$('.archive-item-list-link')[0]).text()).toBe('series_1');
        //         expect($(archiveView.$('.archive-item-list-link')[1]).text()).toBe('series_2');
        //     });
        // });
    });
    describe('Test project render', function () {
    });
});
