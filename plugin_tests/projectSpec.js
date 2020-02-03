girderTest.importPlugin('SAIP');
girderTest.startApp();

$(function () {
    var projects;
    describe('setup', function () {
        it('create the admin user', function () {
            girderTest.createUser(
                'miaot2', 'miaot2@nih.gov', 'Admin', 'Admin', 'testpassword')();
        });
        it('load project of user miaot2', function () {
            runs(function () {
                girder.rest.restRequest({
                    url: 'SAIP/miaot2/projects'
                }).then(function (resp) {
                    projects = resp;
                    return null;
                });
            });
            waitsFor(function () {
                return projects !== undefined;
            });
            girderTest.waitForLoad();
            runs(function () {
                expect(projects).toBeDefined();
            });
        });
    });

    describe('Test project render', function () {
        var girder, SAIP, ProjectsViewer, SAIPHierarchyBreadcrumbView,
            SAIPHierarchyBreadcrumbObjects, $breadcrumbViewEl, $viewerEl, viewer, BreadcrumbView;

        beforeEach(function () {
            girder = window.girder;
            SAIP = girder.plugins.SAIP;
            ProjectsViewer = SAIP.views.SAIPProjects;
            SAIPHierarchyBreadcrumbView = SAIP.views.SAIPHierarchyBreadcrumbView;
        });

        it('Load projects', function () {
            $('<div id = "projects"/>').appendTo('body')
                .css({
                    width: '400px',
                    height: '300px'
                });

            $breadcrumbViewEl = $('<div class = "g-hierarchy-breadcrumb-bar"/>').appendTo('#projects');
            $viewerEl = $('<div class = "g-folder-list-container"/>').appendTo('#projects');

            SAIPHierarchyBreadcrumbObjects = [{'object': {'name': 'SAIP'}, 'type': 'SAIP'}];
            BreadcrumbView = new SAIPHierarchyBreadcrumbView({
                el: $breadcrumbViewEl,
                parentView: null,
                objects: SAIPHierarchyBreadcrumbObjects
            });
            viewer = new ProjectsViewer({
                el: $viewerEl,
                projectsFolder: projects,
                parentView: null,
                currentUser: girder.auth.getCurrentUser(),
                SAIPHierarchyBreadcrumbObjects: SAIPHierarchyBreadcrumbObjects,
                hierarchyBreadcrumbView: BreadcrumbView
            });
            waitsFor(function () {
                return $('#projects').length >= 1;
            }, 'viewer to render');

            runs(function () {
                expect(viewer.currentUser).toBeDefined();
                expect($('.breadcrumb').children().length).toBe(1);
                expect($('.g-folder-list-projects').length).toBe(1);
                expect($('.g-folder-list-projects .SAIP-folder-list-entry').length).toBe(446);
            });
        });

        it('Click on project', function () {
            runs(function () {
                $($('.g-folder-list-projects .SAIP-folder-list-entry a.SAIP-folder-list-link-projects')[0]).click();
            });
            waitsFor(function () {
                return $('.g-folder-list-experiments').children().length >= 1;
            }, 'click on first project, experiment to render');
            runs(function () {
                expect($('.breadcrumb').children().length).toBe(2);
                expect($('.g-folder-list-experiments .SAIP-folder-list-entry').length).toBe(1);
            });
        });
    });
});
