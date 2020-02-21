import Model from 'girder/models/Model';
import 'girder/utilities/S3UploadHandler'; // imported for side effect

var FileModel = Model.extend({
    resourceName: 'Archive',
    archive: null,
    type: 'slices'
});

export default FileModel;
