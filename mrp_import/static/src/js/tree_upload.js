odoo.define('mrp_import.upload.mixin', function (require) {
"use strict";

    var core = require('web.core');
    var _t = core._t;

    var qweb = core.qweb;

    var UploadMRPMixin = {

        start: function () {
            // define a unique uploadId and a callback method
            this.fileUploadID = _.uniqueId('mrp_file_upload');
            $(window).on(this.fileUploadID, this._onFileUploaded.bind(this));
            return this._super.apply(this, arguments);
        },

        _onAddAttachment: function (ev) {
            // Auto submit form once we've selected an attachment
            var $input = $(ev.currentTarget).find('input.o_input_file');
            if ($input.val() !== '') {
                var $binaryForm = this.$('.o_mrp_upload form.o_form_binary_form');
                $binaryForm.submit();
            }
        },

        _onFileUploaded: function () {
            // Callback once attachment have been created
            var self = this;
            var attachments = Array.prototype.slice.call(arguments, 1);
            // Get id from result
            var attachent_ids = attachments.reduce(function(filtered, record) {
                if (record.id) {
                    filtered.push(record.id);
                }
                return filtered;
            }, []);
            return this._rpc({
                model: 'mrp.bom',
                method: 'update_bom_from_attachment',
                args: ["", attachent_ids],
                context: this.initialState.context,
            }).then(function(result) {
                self.do_action(result);
            });
        },

        _onUpload: function (event) {
            var self = this;
            // If hidden upload form don't exists, create it
            var $formContainer = this.$('.o_content').find('.o_mrp_upload');
            if (!$formContainer.length) {
                $formContainer = $(qweb.render('mrp_import.MRPHiddenUploadForm', {widget: this}));
                $formContainer.appendTo(this.$('.o_content'));
            }
            // Trigger the input to select a file
            this.$('.o_mrp_upload .o_input_file').click();
        },
    }
    return UploadMRPMixin;
});


odoo.define('mrp.bom.tree', function (require) {
"use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var UploadMRPMixin = require('mrp_import.upload.mixin');
    var viewRegistry = require('web.view_registry');

    var MRPListController = ListController.extend(UploadMRPMixin, {
        buttons_template: 'MRPListView.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_upload': '_onUpload',
            'change .o_mrp_upload .o_form_binary_form': '_onAddAttachment',
        }),
    });

    var MRPListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: MRPListController,
        }),
    });

    viewRegistry.add('mrp_tree', MRPListView);
});
