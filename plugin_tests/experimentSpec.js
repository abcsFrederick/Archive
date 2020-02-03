girderTest.importPlugin('SAIP');
girderTest.startApp();

$(function () {
    var experiments;
    describe('setup', function () {
        it('create the admin user', function () {
            girderTest.createUser(
                'miaot2', 'miaot2@nih.gov', 'Admin', 'Admin', 'testpassword')();
        });
        it('load experiments of #1', function () {
            runs(function () {
                girder.rest.restRequest({
                    url: 'SAIP/1/experiments'
                }).then(function (resp) {
                    experiments = resp;
                    return null;
                });
            });
            waitsFor(function () {
                return experiments !== undefined;
            });
            girderTest.waitForLoad();
            runs(function () {
                expect(experiments).toBeDefined();
            });
        });
    });

    describe('Test experiment render', function () {
        var girder, SAIP, ExperimentsViewer, SAIPHierarchyBreadcrumbView,
            SAIPHierarchyBreadcrumbObjects, $breadcrumbViewEl, $viewerEl, viewer, BreadcrumbView;

        beforeEach(function () {
            girder = window.girder;
            SAIP = girder.plugins.SAIP;
            ExperimentsViewer = SAIP.views.SAIPExperiments;
            SAIPHierarchyBreadcrumbView = SAIP.views.SAIPHierarchyBreadcrumbView;
        });

        it('Load experiments', function () {
            $('<div id = "experiments"/>').appendTo('body')
                .css({
                    width: '400px',
                    height: '300px'
                });

            $breadcrumbViewEl = $('<div class = "g-hierarchy-breadcrumb-bar"/>').appendTo('#experiments');
            $viewerEl = $('<div class = "g-folder-list-container"/>').appendTo('#experiments');

            SAIPHierarchyBreadcrumbObjects = [{'object': {'name': 'SAIP'}, 'type': 'SAIP'}, {'object': {'name': 's'}, 'type': 'project'}];
            BreadcrumbView = new SAIPHierarchyBreadcrumbView({
                el: $breadcrumbViewEl,
                parentView: null,
                objects: SAIPHierarchyBreadcrumbObjects
            });
            viewer = new ExperimentsViewer({
                el: $viewerEl,
                experimentsFolder: experiments,
                parentView: null,
                currentUser: girder.auth.getCurrentUser(),
                SAIPHierarchyBreadcrumbObjects: SAIPHierarchyBreadcrumbObjects,
                hierarchyBreadcrumbView: BreadcrumbView
            });
            waitsFor(function () {
                return $('#experiments').length >= 1;
            }, 'viewer to render');

            runs(function () {
                expect(viewer.currentUser).toBeDefined();
                expect($('.breadcrumb').children().length).toBe(2);
                expect($('.g-folder-list-experiments').length).toBe(1);
                expect($('.g-folder-list-experiments .SAIP-folder-list-entry').length).toBe(1);
            });
        });

        it('Click on experiment', function () {
            runs(function () {
                $($('.g-folder-list-experiments .SAIP-folder-list-entry a.SAIP-folder-list-link-experiments')[0]).click();
            });
            waitsFor(function () {
                return $('.g-folder-list-patients .g-folder-list').children().length >= 1;
            }, 'click on first experiment, patients to render');
            runs(function () {
                expect($('.breadcrumb').children().length).toBe(3);
                expect($('.g-folder-list-patients .SAIP-folder-list-entry').length).toBe(10);
            });
        });
    });
});
