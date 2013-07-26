var directiveTemplateRoot = "/static/js/directive_templates/";
angular.module('XPBoard').directive(
  'stickyColumn', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        items: "=items",
        title: "=title"
      },
      templateUrl: directiveTemplateRoot + "sticky_column.html",
      link: function(scope, element, attrs) {
      }
    }
  }
).directive(
  'sticky', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        data: "=data"
      },
      templateUrl: directiveTemplateRoot + "sticky.html",
      link: function(scope, element, attrs) {
        
      }
    }
  }
);
                                    
