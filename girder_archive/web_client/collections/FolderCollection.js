import Collection from '@girder/core/collections/Collection';

import FolderModel from '../models/FolderModel';

var FolderCollection = Collection.extend({
    resourceName: 'Archive',
    model: FolderModel,

    pageLimit: 10000,

    rename: function (opts) {
        this.resourceName = this.resourceName + '/' + opts.archive + '/' + opts.type;
    }
});

export default FolderCollection;
