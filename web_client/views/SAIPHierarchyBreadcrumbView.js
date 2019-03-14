import View from 'girder/views/View';
import HierarchyBreadcrumbTemplate from '../templates/HierarchyBreadcrumbTemplate.pug';
var SAIPHierarchyBreadcrumbView = View.extend({
    events: {
        'click a.g-breadcrumb-link': function (event) {
            var link = $(event.currentTarget);
            this.trigger('g:breadcrumbClicked', parseInt(link.attr('g-index'), 10));
        }
    },

    initialize: function (settings) {
        this.objects = settings.objects;
        this.render()
    },

    render: function () {
        // Clone the array so we don't alter the instance's copy
        var objects = this.objects.slice(0);

        console.log(objects)
        console.log('middle');
        // Pop off the last object, it refers to the currently viewed
        // object and should be the "active" class, and not a link.
        var active = objects.pop();

        // var descriptionText = $(renderMarkdown(
        //     active.get('description') || '')).text();
        console.log(active);
        this.$el.html(HierarchyBreadcrumbTemplate({
            links: objects,
            current: active,
            //descriptionText: descriptionText
        }));

        return this;
    }
});
export default SAIPHierarchyBreadcrumbView