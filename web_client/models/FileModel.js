import _ from 'underscore';

import FolderModel from 'girder/models/FolderModel';
import ItemModel from 'girder/models/ItemModel';
import Model from 'girder/models/Model';
import { restRequest, uploadHandlers, getUploadChunkSize } from 'girder/rest';
import 'girder/utilities/S3UploadHandler'; // imported for side effect

var FileModel = Model.extend({
    resourceName: 'Archive',
    archive: null,
    type: 'slices',
});

export default FileModel;
