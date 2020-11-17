import Model from '@girder/core/models/Model';
import '@girder/core/utilities/S3UploadHandler'; // imported for side effect

var FileModel = Model.extend({
    resourceName: 'Archive',
    archive: null,
    type: 'slices'
});

export default FileModel;
