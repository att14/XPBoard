var directiveTemplateRoot = '/static/js/directive_templates/';
angular.module('XPBoard').directive(
  'stickyColumnView', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ticketsByTitle: '=ticketsByTitle'
      },
      templateUrl: directiveTemplateRoot + 'sticky_column_view.html',
      link: function(scope) {}
    }
  }
).directive(
  'stickyColumn', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        tickets: '=tickets',
        title: '=title'
      },
      templateUrl: directiveTemplateRoot + 'sticky_column.html',
      link: function(scope, element, attrs) {}
    }
  }
).directive(
  'sticky', ['URLGenerator', 'status', function(URLGenerator) {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ticket: '=ticket'
      },
      templateUrl: directiveTemplateRoot + 'sticky.html',
      link: function(scope, element, attrs) {
        scope.URLGenerator = URLGenerator;
        console.log(scope.ticket);
      }
    }
  }]
).directive(
  'ticketTable', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        tickets: '=tickets',
        title: '=title'
      },
      templateUrl: directiveTemplateRoot + 'ticket_table.html',
      link: function(scope) {}
    }
  }
);
                                    
