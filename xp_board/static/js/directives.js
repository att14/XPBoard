var directiveTemplateRoot = '/static/js/directive_templates/';
angular.module('XPBoard').directive(
  'stickyColumnView', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        itemsByTitle: '=itemsByTitle'
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
        items: '=items',
        title: '=title'
      },
      templateUrl: directiveTemplateRoot + 'sticky_column.html',
      link: function(scope, element, attrs) {}
    }
  }
).directive(
  'sticky', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        data: '=data'
      },
      templateUrl: directiveTemplateRoot + 'sticky.html',
      link: function(scope, element, attrs) {}
    }
  }
).directive(
  'userTable', function() {
      return {
        restrict: 'E',
        replace: true,
        scope: {
          username: '=username',
          ownedTickets: '=ownedTickets'
        },
        templateUrl: directiveTemplateRoot + 'user_table.html',
        link: function(scope) {
          scope.ticketsByStatus = _.groupBy(scope.ownedTickets, 'status');
        }
      }
    }
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
                                    
