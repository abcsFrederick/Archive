girderTest.importPlugin('Archive');
girderTest.startApp();

$(function () {
    describe('setup', function () {
        it('create the admin user', function () {
            girderTest.createUser(
                'miaot2', 'miaot2@nih.gov', 'Admin', 'Admin', 'testpassword')();
        });
    });
    describe('Test project render', function () {
    });
});
