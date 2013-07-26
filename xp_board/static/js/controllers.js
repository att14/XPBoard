// var usernames = [
//   'atribone', 'imalison', 'anthony', 'sraveend', 'dersek', 'ssridhar',
//   'yoann', 'selston', 'cheng', 'bthiell', 'arvin', 'ychan', 'yli',
//   'clee', 'matthew', 'ywchen', 'joshua'
// ];
// $scope.statuses = ["New", "Assigned", "In Review", "Ship-It", "On Prod"]

TicketsByStatusCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByStatus = _.groupBy(TicketData.tickets, 'status');
}];

TicketsByOwnerCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
}];


ReviewsByUserCtrl = ['$scope', function($scope) {

}];

UserStatusCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.tickets = TicketData.ticketsByUsernames(['atribone']);
  $scope.title = 'Derp';
}]
