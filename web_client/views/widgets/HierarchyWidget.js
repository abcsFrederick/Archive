import View from 'girder/views/View';
import { getModelClassByName, renderMarkdown, formatCount, capitalize, formatSize } from 'girder/misc';

import HierarchyBreadcrumbTemplate from '../../templates/widgets/HierarchyBreadcrumbTemplate.pug';
import HierarchyWidgetTemplate from '../../templates/widgets/hierarchyWidget.pug';
import FolderListWidget from './FolderListWidget';
import ItemListWidget from './ItemListWidget';

var HierarchyBreadcrumbView = View.extend({
    events: {
        'click a.g-breadcrumb-link': function (event) {
            var link = $(event.currentTarget);
            this.trigger('g:breadcrumbClicked', parseInt(link.attr('g-index'), 10));
        }
    },

    initialize: function (settings) {
        this.objects = settings.objects;
    },

    render: function () {
        // Clone the array so we don't alter the instance's copy
        var objects = this.objects.slice(0);

        // Pop off the last object, it refers to the currently viewed
        // object and should be the "active" class, and not a link.
        var active = objects.pop();
        this.$el.html(HierarchyBreadcrumbTemplate({
            links: objects,
            current: active
        }));

        return this;
    }
});

var HierarchyWidget = View.extend({
    initialize: function (settings) {
        this.type = settings.type;

        this.breadcrumbs = [{'object': {'name': 'Projects'},
                             'type': 'projects'
                            }];
        // Initialize the breadcrumb bar state
        this.breadcrumbView = new HierarchyBreadcrumbView({
            objects: this.breadcrumbs,
            parentView: this
        });
        this.breadcrumbView.on('g:breadcrumbClicked', function (idx) {
            this.breadcrumbs = this.breadcrumbs.slice(0, idx + 1);
            this.setCurrentModel(this.breadcrumbs[idx]);
        }, this);

        this.folderListView = new FolderListWidget({
            type: this.type,
            data: {},
            parentView: this
        });

        this.folderListView.on('g:folderClicked', function (folder) {
            this.descend(folder);

        }, this).off('g:checkboxesChanged')
            .on('g:checkboxesChanged', this.updateChecked, this)
            .off('g:changed').on('g:changed', function () {
                this.folderCount = this.folderListView.collection.length;
                // this._childCountCheck();
            }, this);
        this.render();
    },
    render() {
        this.$el.html(HierarchyWidgetTemplate());
        this.breadcrumbView.setElement(this.$('.g-hierarchy-breadcrumb-bar>ol')).render();
        this.folderListView.setElement(this.$('.g-folder-list-container')).render();
        if (this.type === 'series') {
            this.itemListView.setElement(this.$('.g-item-list-container')).render();
        }
    },
    setCurrentModel: function (parent, opts) {
        opts = opts || {};
        this.type = parent.type;

        this.breadcrumbView.objects = this.breadcrumbs;

        if (this.type === 'series') {
            if (!this.itemListView) {
                this.itemListView = new ItemListWidget({
                    type: this.type,
                    data: {'id': parent.id},
                    parentView: this
                });
            } else {
                this.itemListView.initialize({
                    type: this.type,
                    data: {'id': parent.id},
                    parentView: this
                });
            }
            // FIXME: render folder with empty
            this.folderListView.initialize({
                type: this.type,
                data: {'id': -1},
                parentView: this
            });;
        } else {
            this.folderListView.initialize({
                type: this.type,
                data: {'id': parent.id},
                parentView: this
            });
        }

        this.render();
        this.trigger('g:setCurrentModel');
    },
    descend: function (folder) {
        if (folder.collection.resourceName === 'Archive/SAIP/projects') {
            folder.type = 'experiments';
            folder.id = folder.get('nci_projects_id');
            this.breadcrumbs.push(folder);
            this.setCurrentModel(folder);
        } else if (folder.collection.resourceName === 'Archive/SAIP/experiments') {
            folder.type = 'patients';
            folder.id = folder.get('id');
            this.breadcrumbs.push(folder);
            this.setCurrentModel(folder);
        } else if (folder.collection.resourceName === 'Archive/SAIP/patients') {
            folder.type = 'studies';
            folder.id = folder.get('id');
            this.breadcrumbs.push(folder);
            this.setCurrentModel(folder);
        } else if (folder.collection.resourceName === 'Archive/SAIP/studies') {
            folder.type = 'series';
            folder.id = folder.get('id');
            this.breadcrumbs.push(folder);
            this.setCurrentModel(folder);
        }
    },
});

export default HierarchyWidget;
